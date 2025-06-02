from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.deps import get_db, CurrentAdmin          # ⬅
from app.schemas import ProductIn, CategoryIn, ProductOut
from app.rabit import publish_event
from app.iam_client import stub
from datetime import datetime


router = APIRouter(prefix="/admin", tags=["admin"])

# ---------- محصولات ----------

@router.post("/products-add", status_code=status.HTTP_201_CREATED, response_model=ProductOut)
async def add_product(data: ProductIn, db=Depends(get_db), admin=Depends(CurrentAdmin)):
    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()  # ← افزودن زمان ساخت
    res = await db.products.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    await publish_event("product.created", {"product_id": doc["_id"], "admin_id": admin["id"]})
    return ProductOut(**doc)

@router.delete("/products-delete/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, db=Depends(get_db), admin=Depends(CurrentAdmin)):
    res = await db.products.delete_one({"_id": ObjectId(product_id)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Product not found")
    await publish_event("product.deleted", {"product_id": product_id, "admin_id": admin["id"]})

# ---------- کاربران ----------

@router.delete("/users-delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, admin=Depends(CurrentAdmin)):
    from app.iam import iam_pb2
    try:
        await stub.DeleteUser(iam_pb2.DeleteUserRequest(user_id=user_id))
    except Exception:
        raise HTTPException(502, "IAM gRPC unavailable")
    await publish_event("user.deleted", {"user_id": user_id, "admin_id": admin["id"]})

@router.patch("/ban-users/{user_id}", status_code=status.HTTP_200_OK)
async def ban_user(user_id: int, admin=Depends(CurrentAdmin)):
    from app.iam import iam_pb2
    try:
        await stub.BanUser(iam_pb2.BanUserRequest(user_id=user_id))
    except Exception:
        raise HTTPException(502, "IAM gRPC unavailable")
    await publish_event("user.banned", {"user_id": user_id, "admin_id": admin["id"]})
    return {"detail": "user banned"}


@router.post("/add-categories", status_code=status.HTTP_201_CREATED)
async def add_category(data: CategoryIn, db=Depends(get_db), admin=Depends(CurrentAdmin)):
    doc = data.model_dump()
    res = await db.category.insert_one(doc)
    doc["_id"] = str(res.inserted_id)
    await publish_event("category.created", {"category_id": doc["_id"], "admin_id": admin["id"]})
    return doc
