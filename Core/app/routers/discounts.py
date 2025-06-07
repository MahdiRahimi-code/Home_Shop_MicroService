# app/routers/discounts.py
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime
from app.schemas import DiscountIn, DiscountOut
from app.deps import get_db, CurrentAdmin
from app.routers._utils import fix_objectid
import decimal

router = APIRouter(prefix="/discounts", tags=["discounts"])

@router.post("/", response_model=DiscountOut, status_code=status.HTTP_201_CREATED)
async def add_discount(data: DiscountIn, db=Depends(get_db), admin=Depends(CurrentAdmin)):
    doc = data.model_dump()
    if isinstance(doc.get("percentage"), decimal.Decimal):
        doc["percentage"] = float(doc["percentage"])  
    doc["created_at"] = datetime.utcnow()
    res = await db.discounts.insert_one(doc)
    doc["_id"] = res.inserted_id
    return fix_objectid(doc)

# @router.delete("/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def remove_discount(discount_id: str, db=Depends(get_db), admin=Depends(CurrentAdmin)):
#     # حذفِ دستیِ تخفیف توسط ادمین
#     res = await db.discounts.delete_one({"_id": ObjectId(discount_id)})
#     if res.deleted_count == 0:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Discount not found")


@router.delete("/{discount_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_discount(discount_id: str, db=Depends(get_db), admin=Depends(CurrentAdmin)):
    res = await db.discounts.delete_one({"_id": ObjectId(discount_id)})
    if res.deleted_count == 0:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Discount not found")
    # remove from products
    await db.products.update_many(
        {"discount_id": ObjectId(discount_id)},
        {"$unset": {"discount_id": ""}}
    )
