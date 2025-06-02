from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field

# Helpers ------------------------------------------------
class PyObjectId(ObjectId):
    """For Pydantic <-> BSON conversion"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)


# Mongo-documents ----------------------------------------
class Product(BaseModel):
    id: PyObjectId | None = Field(alias="_id", default=None)
    name: str
    description: str | None = None
    stock_num: int = 0
    rating: float = 0.0
    color: str | None = None
    company: str | None = None
    discount_id: str | None = None
    category_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Category(BaseModel):
    id: PyObjectId | None = Field(alias="_id", default=None)
    name: str
    is_active: bool = True


class WishlistItem(BaseModel):
    id: PyObjectId | None = Field(alias="_id", default=None)
    user_id: int        # از IAM
    product_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Address(BaseModel):
    id: PyObjectId | None = Field(alias="_id", default=None)
    user_id: int
    street: str
    postal_code: str | None = None
    city: str | None = None
    is_default: bool = False


class Payment(BaseModel):
    id: PyObjectId | None = Field(alias="_id", default=None)
    user_id: int
    amount: float
    status: str = "pending"      # pending, paid, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    estimated_settlement: datetime | None = None
