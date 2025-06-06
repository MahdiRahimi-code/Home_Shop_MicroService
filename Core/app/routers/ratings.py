# app/routers/ratings.py
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.schemas import BaseModel
from datetime import datetime
from app.deps import get_db, CurrentUser
# from pydantic import BaseModel, Field
from pydantic import Field



router = APIRouter(prefix="/ratings", tags=["ratings"])

class RateIn(BaseModel):
    product_id: str
    score: int = Field(..., ge=1, le=5)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def rate_product(data: RateIn, db=Depends(get_db), user=Depends(CurrentUser)):
    # ابتدا بررسی کن محصول وجود دارد
    prod = await db.products.find_one({"_id": ObjectId(data.product_id)})
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    # سپس یک رکورد در کلکسیون ratings بگذار
    doc = {
        "user_id": user["id"],
        "product_id": ObjectId(data.product_id),
        "score": data.score,
        "created_at": datetime.utcnow()
    }
    res = await db.ratings.insert_one(doc)
    return {"detail": "rated", "rating_id": str(res.inserted_id)}
