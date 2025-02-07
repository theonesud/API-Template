import pytest
import requests

from config import settings

company_id = 1  # Assuming we're working with company ID 1


@pytest.mark.asyncio
async def test_get_company(access_token):
    response = requests.get(
        f"{settings.BASE_URL}/company/{company_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Company retrieved successfully"
    data = response.json()["data"]
    print(data)


@pytest.mark.asyncio
async def test_update_company(access_token):
    response = requests.put(
        f"{settings.BASE_URL}/company/{company_id}",
        json={
            "name": "Updated Test Company",
            "about": "This is an updated test company description.",
            "calling_phone_numbers": "+1234567890",
            "whatsapp_phone_number": "+1987654321",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Company updated successfully"
    assert response.json()["data"]["company_id"] == company_id
    print(response.json())
