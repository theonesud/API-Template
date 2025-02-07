import uuid
from pprint import pprint

import pytest
import requests
from config import settings

product_id = str(uuid.uuid4())  # Generate a UUID for product_id
product_id = "0c5f630c-8437-4871-9397-9421a12e439a"


@pytest.mark.asyncio
async def test_create_product(access_token):
    global product_id
    response = requests.post(
        f"{settings.BASE_URL}/products",
        json={
            "name": "Product 1",
            "description": "Description for Product 1",
            "price": "100",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.json()}")
    assert response.status_code == 200
    # product_id = response.json()["data"]["product_id"]


@pytest.mark.asyncio
async def test_get_products(access_token):
    response = requests.get(
        f"{settings.BASE_URL}/products",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    pprint(response.json())


@pytest.mark.asyncio
async def test_get_product(access_token):
    global product_id
    response = requests.get(
        f"{settings.BASE_URL}/products/{product_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    pprint(response.json())


@pytest.mark.asyncio
async def test_update_product(access_token):
    global product_id
    response = requests.put(
        f"{settings.BASE_URL}/products/{product_id}",
        json={
            "name": "Updated Product Name",
            "description": "Updated product description",
        },
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    print(response.json())


@pytest.mark.asyncio
async def test_delete_product(access_token):
    global product_id
    response = requests.delete(
        f"{settings.BASE_URL}/products/{product_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    print(response.json())
