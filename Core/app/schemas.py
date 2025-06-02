from pydantic import BaseModel, Field, EmailStr, PositiveFloat
from datetime import datetime
from typing import List, Optional

class ProductOut(BaseModel):
    id: str = Field(alias="_id")
    name: str
    description: str | None = None
    stock_num: int
    rating: float
    color: str | None
    company: str | None
    category_id: str | None
    created_at: datetime

class ProductIn(BaseModel):
    name: str
    description: Optional[str] = ""
    stock_num: int = 0
    rating: float = 0.0
    color: Optional[str] = None
    company: Optional[str] = None
    category_id: Optional[str] = None
    discount_id: Optional[str] = None
    is_active: bool = True

class CategoryIn(BaseModel):
    name: str = Field(..., max_length=100)
    is_active: bool = True

class CategoryOut(BaseModel):
    id: str = Field(alias="_id")
    name: str
    is_active: bool

class WishlistOut(BaseModel):
    product_ids: List[str]

class AddressIn(BaseModel):
    street: str
    postal_code: str | None = None
    city: str | None = None
    is_default: bool = False

class AddressOut(AddressIn):
    id: str = Field(alias="_id")

class PaymentOut(BaseModel):
    id: str = Field(alias="_id")
    amount: float
    status: str
    created_at: datetime
    estimated_settlement: datetime | None = None

from datetime import datetime

class ProductOut(BaseModel):
    id: str = Field(..., alias="_id")  # ← تبدیل ObjectId به str
    name: str
    description: str
    stock_num: int
    rating: float
    color: str
    company: str
    category_id: str
    discount_id: str
    is_active: bool
    created_at: Optional[datetime]

    class Config:
        allow_population_by_field_name = True