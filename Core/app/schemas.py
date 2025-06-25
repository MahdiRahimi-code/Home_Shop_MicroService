# app/schemas.py

from pydantic import BaseModel, Field, condecimal, validator
from datetime import datetime, timezone
from typing import List, Optional

# --- مدل‌های محصول ---

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
    price: condecimal(gt=0, max_digits=12, decimal_places=2) 
    

class AddressIn(BaseModel):
    street: str
    postal_code: Optional[str] = None
    city: Optional[str] = None
    is_default: bool = False

class AddressOut(AddressIn):
    id: str = Field(alias="_id")


# --- Payment ---
class PaymentOut(BaseModel):
    id: str = Field(alias="_id")
    amount: float
    status: str
    created_at: datetime
    estimated_settlement: Optional[datetime] = None


class ProductOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    description: Optional[str] = None
    stock_num: int
    rating: float
    color: Optional[str]
    company: Optional[str]
    category_id: Optional[str]
    discount_id: Optional[str]
    is_active: bool
    price: condecimal(gt=0, max_digits=12, decimal_places=2)
    created_at: datetime

    class Config:
        allow_population_by_field_name = True



class BasketItem(BaseModel):
    product_id: str
    quantity: int

class ReceiptOut(BaseModel):
    id: str             
    user_id: int
    items: List[BasketItem]
    total_price: float
    address_id: str
    created_at: datetime
    estimated_delivery: datetime
    status: str

    class Config:
        model_config = {
            "populate_by_name": True,
            "extra": "ignore"
        }



class CategoryIn(BaseModel):
    name: str
    is_active: bool = True

class CategoryOut(BaseModel):
    id: str = Field(..., alias="_id")
    name: str
    is_active: bool

    class Config:
        allow_population_by_field_name = True

# --- مدل‌های تخفیف ---

class DiscountIn(BaseModel):
    code: str
    percentage: condecimal(gt=0, lt=100, max_digits=5, decimal_places=2)
    max_uses: int = 1
    expiration_date: datetime
    is_active: bool = True

    @validator("expiration_date")
    def must_be_future(v: datetime):
        if v <= datetime.now(timezone.utc):
            raise ValueError("expiration_date must be in the future")
        return v
    # def must_be_future(cls, v):
    #     from datetime import datetime
    #     if v <= datetime.utcnow():
    #         raise ValueError("expiration_date must be after now")
    #     return v

class DiscountOut(DiscountIn):
    id: str = Field(..., alias="_id")

    class Config:
        allow_population_by_field_name = True

# --- مدل‌های بازبینی (Review) ---

class ReviewIn(BaseModel):
    product_id: str
    score: int = Field(..., ge=1, le=5)
    content: Optional[str] = None

class ReviewOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: int
    product_id: str
    score: int
    content: Optional[str]
    created_at: datetime

    class Config:
        allow_population_by_field_name = True

# --- مدل‌های سبد خرید (Basket) ---

class BasketItem(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)

class BasketOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: int
    items: List[BasketItem]
    total_price: condecimal(gt=0, max_digits=12, decimal_places=2)
    created_at: datetime

    class Config:
        allow_population_by_field_name = True

# --- مدل کیف پول (Wallet) ---

class WalletOut(BaseModel):
    user_id: int
    balance: condecimal(ge=0, max_digits=14, decimal_places=2)

# --- مدل فاکتور (Receipt) ---

class ReceiptOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: int
    items: List[BasketItem]
    total_price: condecimal(gt=0, max_digits=12, decimal_places=2)
    address_id: str
    created_at: datetime
    estimated_delivery: datetime
    status: str

    class Config:
        allow_population_by_field_name = True


from typing import List

class WishlistOut(BaseModel):
    product_ids: List[str]


# # app/schemas.py

# from pydantic import BaseModel, Field
# from datetime import datetime
# from typing import List, Optional

# class ProductOut(BaseModel):
#     id: str = Field(..., alias="_id")         # ObjectId تبدیل‌شده به str
#     name: str
#     description: Optional[str] = None
#     stock_num: int
#     rating: float
#     color: Optional[str] = None
#     company: Optional[str] = None
#     category_id: Optional[str]
#     discount_id: Optional[str]
#     is_active: bool
#     created_at: datetime

#     class Config:
#         allow_population_by_field_name = True


# class ProductIn(BaseModel):
#     name: str
#     description: Optional[str] = ""
#     stock_num: int = 0
#     rating: float = 0.0
#     color: Optional[str] = None
#     company: Optional[str] = None
#     category_id: Optional[str] = None
#     discount_id: Optional[str] = None
#     is_active: bool = True


# class CategoryIn(BaseModel):
#     name: str
#     is_active: bool = True


# class CategoryOut(BaseModel):
#     id: str = Field(..., alias="_id")
#     name: str
#     is_active: bool

#     class Config:
#         allow_population_by_field_name = True


# class WishlistOut(BaseModel):
#     product_ids: List[str]


# class AddressIn(BaseModel):
#     street: str
#     postal_code: Optional[str] = None
#     city: Optional[str] = None
#     is_default: bool = False


# class AddressOut(AddressIn):
#     id: str = Field(..., alias="_id")

#     class Config:
#         allow_population_by_field_name = True


# class PaymentOut(BaseModel):
#     id: str = Field(..., alias="_id")
#     amount: float
#     status: str
#     created_at: datetime
#     estimated_settlement: Optional[datetime] = None

#     class Config:
#         allow_population_by_field_name = True



#------------------------------------


# from pydantic import BaseModel, Field, EmailStr, PositiveFloat
# from datetime import datetime
# from typing import List, Optional

# class ProductOut(BaseModel):
#     id: str = Field(alias="_id")
#     name: str
#     description: str | None = None
#     stock_num: int
#     rating: float
#     color: str | None
#     company: str | None
#     category_id: str | None
#     created_at: datetime

# class ProductIn(BaseModel):
#     name: str
#     description: Optional[str] = ""
#     stock_num: int = 0
#     rating: float = 0.0
#     color: Optional[str] = None
#     company: Optional[str] = None
#     category_id: Optional[str] = None
#     discount_id: Optional[str] = None
#     is_active: bool = True

# class CategoryIn(BaseModel):
#     name: str = Field(..., max_length=100)
#     is_active: bool = True

# class CategoryOut(BaseModel):
#     id: str = Field(alias="_id")
#     name: str
#     is_active: bool

# class WishlistOut(BaseModel):
#     product_ids: List[str]

# class AddressIn(BaseModel):
#     street: str
#     postal_code: str | None = None
#     city: str | None = None
#     is_default: bool = False

# class AddressOut(AddressIn):
#     id: str = Field(alias="_id")

# class PaymentOut(BaseModel):
#     id: str = Field(alias="_id")
#     amount: float
#     status: str
#     created_at: datetime
#     estimated_settlement: datetime | None = None

# from datetime import datetime

# class ProductOut(BaseModel):
#     id: str = Field(..., alias="_id")  # ← تبدیل ObjectId به str
#     name: str
#     description: str
#     stock_num: int
#     rating: float
#     color: str
#     company: str
#     category_id: str
#     discount_id: str
#     is_active: bool
#     created_at: Optional[datetime]

#     class Config:
#         allow_population_by_field_name = True