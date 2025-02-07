from datetime import datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field


class EditCompanyRequest(BaseModel):
    name: Optional[str] = None
    about: Optional[str] = None
    calling_phone_numbers: Optional[str] = None
    whatsapp_phone_number: Optional[str] = None


class GoogleToken(BaseModel):
    google_token: str


class ProductRequest(BaseModel):
    name: str
    description: str
    price: str


class EditProductRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    deleted: Optional[bool] = None
