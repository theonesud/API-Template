from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic_settings import BaseSettings
from starlette.config import Config

from core.log import setup_logger

load_dotenv(verbose=True, override=True)


class Settings(BaseSettings):
    ENV: str
    ASYNCPG_URL: str
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SLACK_ERROR_CHANNEL: str
    SLACK_INFO_CHANNEL: str
    SLACK_WEBHOOK_URL_INFO: str
    SLACK_WEBHOOK_URL_ERROR: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    SUPERUSER_EMAIL: str
    SUPERUSER_NAME: str
    API_SECRET_KEY: str
    FRONTEND_URL: str
    BASE_URL: str
    # AWS_ACCESS_KEY: str
    # AWS_SECRET_KEY: str
    # AWS_REGION: str


settings = Settings()
app_logger = setup_logger(settings=settings)

# boto3_session = aioboto3.Session(
#     aws_access_key_id=settings.aws_access_key,
#     aws_secret_access_key=settings.aws_secret_key,
#     region_name=settings.aws_region,
# )


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
oauth = OAuth(
    Config(
        environ={
            "GOOGLE_CLIENT_ID": settings.GOOGLE_CLIENT_ID,
            "GOOGLE_CLIENT_SECRET": settings.GOOGLE_CLIENT_SECRET,
        }  # type: ignore
    )
)
oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/token")
