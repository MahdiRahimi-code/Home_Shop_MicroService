from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.deps import get_db, CurrentUser
from app.schemas import WishlistOut

router = APIRouter(prefix="/wishlist", tags=["wishlist"])

@router.get("/", response_model=WishlistOut)
async def visit_wishlist(db=Depends(get_db), user=Depends(CurrentUser)):
    cursor = db.wishlist.find({"user_id": user["id"]})
    product_ids = [str(item["product_id"]) async for item in cursor]
    return {"product_ids": product_ids}

@router.post("/add-product-to-wishlist/{product_id}", status_code=status.HTTP_201_CREATED)
async def add_product_to_wishlist(product_id: str, db=Depends(get_db), user=Depends(CurrentUser)):
    pid = ObjectId(product_id)
    exists = await db.wishlist.find_one({"user_id": user["id"], "product_id": pid})
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already in wishlist")
    await db.wishlist.insert_one({"user_id": user["id"], "product_id": pid})
    return {"detail": "added"}

@router.delete("/delete-product-from-wishlist/{product_id}")
async def remove_product_from_wishlist(product_id: str, db=Depends(get_db), user=Depends(CurrentUser)):
    result = await db.wishlist.delete_one({"user_id": user["id"], "product_id": ObjectId(product_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return {"detail": "removed"}
