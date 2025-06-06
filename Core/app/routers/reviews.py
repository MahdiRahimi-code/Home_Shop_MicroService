# app/routers/reviews.py
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime
from app.schemas import ReviewIn, ReviewOut
from app.deps import get_db, CurrentUser, CurrentAdmin
from app.routers._utils import fix_objectid

router = APIRouter(prefix="/reviews", tags=["reviews"])

# کاربر می‌تواند یک نظر برای محصول ثبت کند
@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def add_review(data: ReviewIn, db=Depends(get_db), user=Depends(CurrentUser)):
    # ابتدا مطمئن شویم محصول وجود دارد
    prod = await db.products.find_one({"_id": ObjectId(data.product_id)})
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    doc = {
        "user_id": user["id"],
        "product_id": ObjectId(data.product_id),
        "score": data.score,
        "content": data.content,
        "created_at": datetime.utcnow()
    }
    res = await db.reviews.insert_one(doc)
    doc["_id"] = res.inserted_id
    # برگرداندن خروجی با تبدیل ObjectId به str
    return fix_objectid(doc)

# کاربر یا همه می‌توانند نظرات یک محصول را ببیند
@router.get("/product/{product_id}", response_model=list[ReviewOut])
async def get_product_reviews(product_id: str, db=Depends(get_db)):
    docs = []
    cursor = db.reviews.find({"product_id": ObjectId(product_id)}).sort("created_at", -1)
    async for doc in cursor:
        docs.append(fix_objectid(doc))
    return docs

# ادمین می‌تواند هر نظر را حذف کند
@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(review_id: str, db=Depends(get_db), admin=Depends(CurrentAdmin)):
    res = await db.reviews.delete_one({"_id": ObjectId(review_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
