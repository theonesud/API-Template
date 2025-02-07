import pytest
import requests

from config import settings

BASE_URL = f"{settings.BASE_URL}/user"


@pytest.mark.asyncio
async def test_token():
    response = requests.post(
        f"{BASE_URL}/token",
        json={
            "google_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6ImIyNjIwZDVlN2YxMzJiNTJhZmU4ODc1Y2RmMzc3NmMwNjQyNDlkMDQiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiIzMzQzNjgwMjk0MDQtNWxsYnAydHU2OGhkMHBxZm5xc3FnYXFtcWxnbzFtOWIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiIzMzQzNjgwMjk0MDQtNWxsYnAydHU2OGhkMHBxZm5xc3FnYXFtcWxnbzFtOWIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMDI1ODYzMTg5MjA3MDU5MzgxMDQiLCJoZCI6InNoZWVnaHJhbS5jb20iLCJlbWFpbCI6InByYXNoYW50QHNoZWVnaHJhbS5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiYXRfaGFzaCI6IkVtUjZZejYxVnBzdWo0UnEzamNEY1EiLCJuYW1lIjoiUHJhc2hhbnQgU2hhcm1hIiwicGljdHVyZSI6Imh0dHBzOi8vbGgzLmdvb2dsZXVzZXJjb250ZW50LmNvbS9hL0FDZzhvY0xTSHhTR3ZpWVpQRDAzZjh3aHBSRml2Qld3MW1CRUdiWXNaQlNVNEN5U2s5SGN2Zz1zOTYtYyIsImdpdmVuX25hbWUiOiJQcmFzaGFudCIsImZhbWlseV9uYW1lIjoiU2hhcm1hIiwiaWF0IjoxNzI2OTEwMjcyLCJleHAiOjE3MjY5MTM4NzJ9.pT0TuhGrQqcr8bmu3yM578D_NhSN9c3kcAkrmq1SQKo4xlst6Uv-GqTRq6naWbTaoyTcFWEPhhmcObyM7OsaA7qq0ORKi9zxh7THOYjZz1qdOAnwe0IfEt6ewnn6DHT_eSoqyKWW-kjlf7jxeTo16I2tLAJ0X5NLKl04m6VEsPgEeM_GtdlHzCkesCHCi5GPiiv45ztiGXTcl-mJyWe6ZkdsZBMQkgh6ejYY9lxrO0GLvsUZggV7TeLQamkqZofP807-ydeYHKI6Dt2hB4j45lOy_zgCojY0yeSLKAaPIkb_ZiWrZAMTUALzGxVrJC0ugWEQp47XZyouNKJfeTuSQg"
        },
    )
    assert response.status_code == 200
    print(response.json())


@pytest.mark.asyncio
async def test_logout(access_token):
    response = requests.get(
        f"{BASE_URL}/logout", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["msg"] == "Logged out successfully"


@pytest.mark.asyncio
async def test_get_user(access_token):
    response = requests.get(
        f"{BASE_URL}/", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    user_data = response.json()
    print(user_data)
