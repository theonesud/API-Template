from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
from google.auth.transport import requests as google_auth_requests
from google.oauth2 import id_token
from sqlalchemy import insert, select, update

from config import CREDENTIALS_EXCEPTION, app_logger, oauth, oauth2_scheme, settings
from core.slack import send_error_to_slack
from model import db
from model.db import get_session
from model.ql import GoogleToken

router = APIRouter(prefix="/user")


def create_token(data, login_time, type="access"):
    app_logger.info(f"Creating {type} token for {data['name']}")
    if type == "access":
        data["token_type"] = "access"
        data.update(
            {
                "exp": login_time
                + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            }
        )
    elif type == "refresh":
        data["token_type"] = "refresh"
        data.update(
            {
                "exp": login_time
                + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
            }
        )
    else:
        return None
    data.pop("created_at", None)
    data.pop("updated_at", None)
    return jwt.encode(data, settings.API_SECRET_KEY, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, settings.API_SECRET_KEY, algorithms=["HS256"])


async def get_user_from_email(email: str) -> dict:
    query = select(db.User).where(db.User.email == email, db.User.deleted == False)
    async with get_session() as s:
        user = (await s.execute(query)).first()
    if not user:
        app_logger.error(f"User with email {email} not found or deleted")
        raise HTTPException(
            status_code=401, detail="User email not found or is deactivated"
        )
    return {c.name: getattr(user[0], c.name) for c in user[0].__table__.columns}


async def get_user_from_token(token: str = Depends(oauth2_scheme)):
    if settings.ENV == "local":
        payload = {
            "email": settings.SUPERUSER_EMAIL,
            "name": settings.SUPERUSER_NAME,
            "id": 1,
            "token_type": "access",
            "company_id": 1,
        }
    else:
        try:
            payload = decode_token(token)
        except jwt.PyJWTError:
            app_logger.warning("Decoding token failed")
            raise CREDENTIALS_EXCEPTION

        if payload["token_type"] != "access":
            raise HTTPException(status_code=401, detail="Not an access token")
    return payload


async def refresh_helper(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        app_logger.warning("Decoding token failed")
        raise CREDENTIALS_EXCEPTION

    if payload["token_type"] != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user = await get_user_from_email(payload["email"])
    payload.update(user)

    return payload


@router.get("/login")
async def google_login(request: Request):
    try:
        # print(
        #     (
        #         await oauth.google.authorize_redirect(request, settings.FRONTEND_URL)
        #     ).headers
        # )
        # return
        return await oauth.google.authorize_redirect(request, settings.FRONTEND_URL)
    except Exception as e:
        app_logger.exception(f"Error redirecting to Google login: {e}")
        await send_error_to_slack(f"Error redirecting to Google login: {e}")
        return HTTPException(
            status_code=500, detail="Error redirecting to Google login"
        )


@router.post("/token")
async def authenticate_google_token(google_token: GoogleToken):
    try:
        if settings.ENV != "local":
            try:
                request = google_auth_requests.Request()
                resp = id_token.verify_oauth2_token(
                    google_token.google_token,
                    request=request,
                    audience=settings.GOOGLE_CLIENT_ID,
                )
                if resp["iss"] not in [
                    "accounts.google.com",
                    "https://accounts.google.com",
                ]:
                    raise CREDENTIALS_EXCEPTION
            except Exception as e:
                app_logger.error(f"Google token verification failed: {str(e)}")
                raise CREDENTIALS_EXCEPTION

            user_data = {
                "email": resp["email"],
                "name": resp["name"],
                "image": resp.get("picture"),
            }
        else:
            user_data = {
                "email": settings.SUPERUSER_EMAIL,
                "name": settings.SUPERUSER_NAME,
                "image": "https://asdasd",
            }
        login_time = datetime.utcnow()
        user_data.update({"login_time": str(login_time)})
        user = await get_user_from_email(user_data["email"])
        user_data.update(user)
        app_logger.info(f"Creating session for {user_data['name']}")
        query = insert(db.Session).values(
            {"user_id": user["id"], "login_time": login_time}
        )
        async with get_session() as s:
            await s.execute(query)
        return {
            "access_token": create_token(user_data, login_time),
            "refresh_token": create_token(user_data, login_time, "refresh"),
        }
    except Exception as e:
        app_logger.exception(f"Error authenticating Google token: {e}")
        await send_error_to_slack(f"Error authenticating Google token: {e}")
        return HTTPException(
            status_code=500, detail="Error authenticating Google token"
        )


@router.post("/refresh")
async def refresh(user=Depends(refresh_helper)):
    try:
        login_time = datetime.utcnow()
        update_query = (
            update(db.Session)
            .where(
                db.Session.user_id == user["id"],
            )
            .values({"deleted": True})
        )
        insert_query = insert(db.Session).values(
            {"user_id": user["id"], "login_time": login_time}
        )
        async with get_session() as s:
            await s.execute(update_query)
            await s.execute(insert_query)
        app_logger.info(
            f"Expired all old sessions for the user and created a new session for {user['name']}"
        )
        user.pop("login_time")
        user.pop("exp")
        user.update({"login_time": str(login_time)})
        return {"access_token": create_token(user, login_time)}
    except Exception as e:
        app_logger.exception(f"Error refreshing token: {e}")
        await send_error_to_slack(f"Error refreshing token: {e}")
        return HTTPException(status_code=500, detail="Error refreshing token")


@router.get("/logout")
async def logout(user=Depends(get_user_from_token)):
    try:
        query = (
            update(db.Session)
            .where(
                db.Session.user_id == user["id"],
            )
            .values({"deleted": True})
        )
        async with get_session() as s:
            await s.execute(query)
        app_logger.info(f"{user['name']} logged out")
        return {"msg": "Logged out successfully"}
    except Exception as e:
        app_logger.exception(f"Error logging out: {e}")
        await send_error_to_slack(f"Error logging out: {e}")
        return HTTPException(status_code=500, detail="Error logging out")


@router.get("/")
async def get_user(user=Depends(get_user_from_token)):
    try:
        app_logger.info(f"{user['name']} fetched own user details")
        return user
    except Exception as e:
        app_logger.exception(f"Error fetching user details: {e}")
        await send_error_to_slack(f"Error fetching user details: {e}")
        return HTTPException(status_code=500, detail="Error fetching user details")
