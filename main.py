from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from api.auth import router as auth_router
from api.products import router as products_router
from api.settings import router as settings_router
from config import app_logger, settings
from model.db import Base, Company, User, engine, get_session

load_dotenv(verbose=True, override=True)


app = FastAPI(title="API-Template")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SessionMiddleware, secret_key=settings.API_SECRET_KEY)


@app.on_event("startup")
async def startup_event():
    app_logger.debug("Server Starting Up...")


@app.get("/")
async def health():
    app_logger.info("Server is healthy")
    return {"health": "ok"}


@app.get("/reset_db")
async def reset_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        now = datetime.utcnow()
        company = Company(
            name="Test Company",
            about="This is a test company.",
            calling_phone_numbers="+15551234567",
            whatsapp_phone_number="+15557654321",
            created_at=now,
        )
        async with get_session() as session:
            session.add(company)
            await session.flush()  # Flush to get the company ID

            user = User(
                email=settings.SUPERUSER_EMAIL,
                company_id=company.id,
                created_at=now,
            )
            session.add(user)
        return {"msg": "Database reset successfully"}
    except Exception as e:
        app_logger.error(f"Error resetting the database: {e}")
        return HTTPException(status_code=500, detail="Error resetting the database")


@app.on_event("shutdown")
async def shutdown_event():
    app_logger.debug("Server Shutting Down...")


app.include_router(products_router)
app.include_router(auth_router)
app.include_router(settings_router)
