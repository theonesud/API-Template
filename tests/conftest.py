# conftest.py
from datetime import datetime, timedelta

import jwt
import pytest

from config import settings


@pytest.fixture
def access_token():
    login_time = datetime.utcnow()
    exp = login_time + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = {
        "email": settings.SUPERUSER_EMAIL,
        "name": settings.SUPERUSER_NAME,
        "id": 1,
        "company_id": 1,
        "exp": exp,
        "token_type": "access",
    }

    return jwt.encode(token_data, settings.API_SECRET_KEY, algorithm="HS256")
