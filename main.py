import os
import subprocess
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette import status
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from api.auth import router as auth_router
from api.products import router as products_router
from api.settings import router as settings_router
from config import app_logger, settings
from model.db import Base, Company, User, engine, get_session

load_dotenv(verbose=True, override=True)


app = FastAPI(title="API-Template")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    exc_str = f"{exc}".replace("\n", " ").replace("   ", " ")
    app_logger.error(f"{request}: {exc_str}")
    content = {"status_code": 10422, "message": exc_str, "data": None}
    return JSONResponse(
        content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


origins = [settings.FRONTEND_URL, "http://localhost:3000", "http://127.0.0.1:3000"]

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
        # Get database URL from settings
        db_url = settings.ASYNCPG_URL

        # Parse connection info from URL
        # Example URL format: postgresql+asyncpg://user:password@host:port/dbname
        db_info = db_url.replace("postgresql+asyncpg://", "").split("/")
        auth_host = db_info[0].split("@")
        dbname = db_info[1]

        auth = auth_host[0].split(":")
        host_port = auth_host[1].split(":")

        username = auth[0]
        password = auth[1] if len(auth) > 1 else ""
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else "5432"

        # Ensure backup directory exists
        os.makedirs("db_backups", exist_ok=True)

        # Create backup filename with db name and datetime
        backup_filename = f"{dbname}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.sql"
        backup_path = f"db_backups/{backup_filename}"

        # Set environment variable for password to avoid showing in process list
        env = os.environ.copy()
        env["PGPASSWORD"] = password

        # Run pg_dump to create backup
        result = subprocess.run(
            [
                "pg_dump",
                "-h",
                host,
                "-p",
                port,
                "-U",
                username,
                "-F",
                "c",  # Custom format (compressed)
                "-f",
                backup_path,
                dbname,
            ],
            env=env,
            capture_output=True,
        )

        if result.returncode != 0:
            app_logger.error(f"Database backup failed: {result.stderr.decode()}")
            raise Exception(f"Database backup failed: {result.stderr.decode()}")

        app_logger.info(f"Database backed up to {backup_path}")

        # Original reset code
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

        now = datetime.utcnow()

        async with get_session() as session:
            # Initialize company
            company = Company(
                name="Test Company",
                about="This is a test company.",
                created_at=now,
            )

            # Add company
            session.add(company)
            await session.flush()  # Flush to get the company ID

            # Add superuser
            user = User(
                name="Test User",
                gender="Other",
                dob=now,
                email=settings.SUPERUSER_EMAIL,
                company_id=company.id,
                selected_language="en-US",
                selected_model="gpt-4o-mini",
                created_at=now,
            )
            session.add(user)

        app_logger.info("Database reset and initialized successfully")
        return {"message": "Database reset and initialized successfully"}

    except Exception as e:
        app_logger.exception(f"Error resetting database: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error resetting database: {str(e)}"
        )


@app.on_event("shutdown")
async def shutdown_event():
    app_logger.debug("Server Shutting Down...")


app.include_router(products_router)
app.include_router(auth_router)
app.include_router(settings_router)
