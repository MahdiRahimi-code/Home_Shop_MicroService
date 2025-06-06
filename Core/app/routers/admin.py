# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.deps import get_db, CurrentAdmin
from app.schemas import ProductIn, CategoryIn, ProductOut, ReviewOut, DiscountOut
from app.rabit import publish_event
from app.iam_client import stub
from datetime import datetime
from app.routers._utils import fix_objectid 
import decimal

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------- محصولات ----------
# @router.post(
#     "/products-add",
#     status_code=status.HTTP_201_CREATED,
#     response_model=ProductOut
# )
# async def add_product(
#     data: ProductIn,
#     db=Depends(get_db),
#     admin=Depends(CurrentAdmin)
# ):
#     doc = data.model_dump()
#     doc["created_at"] = datetime.utcnow()
#     doc["updated_at"] = datetime.utcnow()
#     res = await db.products.insert_one(doc)
#     doc["_id"] = res.inserted_id
#     await publish_event("product.created", {"product_id": str(doc["_id"]), "admin_id": admin["id"]})
#     return ProductOut(**fix_objectid(doc))


# app/routers/admin.py   (تغییر در تابع add_product)

# app/routers/admin.py

@router.post("/products-add", status_code=status.HTTP_201_CREATED, response_model=ProductOut)
async def add_product(data: ProductIn, db=Depends(get_db), admin=Depends(CurrentAdmin)):
    if data.category_id:
        cat = await db.category.find_one({"_id": ObjectId(data.category_id), "is_active": True})
        if not cat:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Category not found or inactive")

    if data.discount_id:
        disc = await db.discounts.find_one({"_id": ObjectId(data.discount_id), "is_active": True})
        if not disc:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Discount not found or inactive")
        if disc["expiration_date"] <= datetime.utcnow():
            await db.discounts.update_one(
                {"_id": ObjectId(data.discount_id)}, {"$set": {"is_active": False}}
            )
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "Discount expired")

    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = datetime.utcnow()

    if data.category_id:
        doc["category_id"] = ObjectId(data.category_id)
    if data.discount_id:
        doc["discount_id"] = ObjectId(data.discount_id)
    else:
        doc.pop("discount_id", None)

    # 🔥 تبدیل Decimal به float
    if isinstance(doc.get("price"), decimal.Decimal):
        doc["price"] = float(doc["price"])

    res = await db.products.insert_one(doc)
    doc["_id"] = res.inserted_id
    return ProductOut(**fix_objectid(doc))







@router.delete(
    "/products-delete/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(
    product_id: str,
    db=Depends(get_db),
    admin=Depends(CurrentAdmin)
):
    res = await db.products.delete_one({"_id": ObjectId(product_id)})
    if res.deleted_count == 0:
        raise HTTPException(404, "Product not found")
    await publish_event("product.deleted", {"product_id": product_id, "admin_id": admin["id"]})


# ---------- کاربران ----------
@router.delete(
    "/users-delete/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_user(user_id: int, admin=Depends(CurrentAdmin)):
    from app.iam import iam_pb2
    try:
        await stub.DeleteUser(iam_pb2.DeleteUserRequest(user_id=user_id))
    except Exception:
        raise HTTPException(502, "IAM gRPC unavailable")
    await publish_event("user.deleted", {"user_id": user_id, "admin_id": admin["id"]})


@router.patch(
    "/ban-users/{user_id}",
    status_code=status.HTTP_200_OK
)
async def ban_user(user_id: int, admin=Depends(CurrentAdmin)):
    from app.iam import iam_pb2
    try:
        await stub.BanUser(iam_pb2.BanUserRequest(user_id=user_id))
    except Exception:
        raise HTTPException(502, "IAM gRPC unavailable")
    await publish_event("user.banned", {"user_id": user_id, "admin_id": admin["id"]})
    return {"detail": "user banned"}


# ---------- دسته‌بندی ----------
@router.post(
    "/add-categories",
    status_code=status.HTTP_201_CREATED
)
async def add_category(
    data: CategoryIn,
    db=Depends(get_db),
    admin=Depends(CurrentAdmin)
):
    doc = data.model_dump()
    res = await db.category.insert_one(doc)
    doc["_id"] = res.inserted_id
    await publish_event("category.created", {"category_id": str(doc["_id"]), "admin_id": admin["id"]})
    return fix_objectid(doc)


# ---------- دیدن نظرات یک محصول ----------
@router.get("/product-reviews/{product_id}", response_model=list[ReviewOut])
async def admin_visit_product_reviews(product_id: str, db=Depends(get_db), admin=Depends(CurrentAdmin)):
    cursor = db.reviews.find({"product_id": ObjectId(product_id)}).sort("created_at", -1)
    result = []
    async for doc in cursor:
        result.append(fix_objectid(doc))
    return result

# ---------- حذف یک نظر خاص ----------
@router.delete("/product-reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_product_review(review_id: str, db=Depends(get_db), admin=Depends(CurrentAdmin)):
    res = await db.reviews.delete_one({"_id": ObjectId(review_id)})
    if res.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")


@router.get("/discounts", response_model=list[DiscountOut])
async def admin_list_discounts(db=Depends(get_db), admin=Depends(CurrentAdmin)):
    # فقط تخفیف‌های فعال یا حتی همه
    cursor = db.discounts.find({}).sort("expiration_date", 1)
    result = []
    async for doc in cursor:
        result.append(fix_objectid(doc))
    return result



@router.patch(
    "/products/{product_id}/apply-discount/{discount_id}",
    response_model=ProductOut,
    status_code=status.HTTP_200_OK,
)
async def apply_discount_to_product(
    product_id: str,
    discount_id: str,
    db=Depends(get_db),
    admin=Depends(CurrentAdmin),
):
    # 1. Fetch & validate product
    prod = await db.products.find_one({"_id": ObjectId(product_id)})
    if not prod:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Product not found")

    # 2. Fetch & validate discount
    disc = await db.discounts.find_one({"_id": ObjectId(discount_id)})
    if not disc or not disc.get("is_active", False):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Discount not found or inactive")
    if disc["expiration_date"] <= datetime.utcnow():
        # auto-deactivate expired discount
        await db.discounts.update_one(
            {"_id": disc["_id"]},
            {"$set": {"is_active": False}}
        )
        # remove from any products
        await db.products.update_many(
            {"discount_id": disc["_id"]},
            {"$unset": {"discount_id": ""}}
        )
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Discount expired")

    # 3. Apply it
    await db.products.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"discount_id": ObjectId(discount_id)}}
    )
    updated = await db.products.find_one({"_id": ObjectId(product_id)})
    return ProductOut(**fix_objectid(updated))




# from fastapi import APIRouter, Depends, HTTPException, status
# from bson import ObjectId
# from app.deps import get_db, CurrentAdmin          # ⬅
# from app.schemas import ProductIn, CategoryIn, ProductOut
# from app.rabit import publish_event
# from app.iam_client import stub
# from datetime import datetime


# router = APIRouter(prefix="/admin", tags=["admin"])

# # ---------- محصولات ----------

# @router.post("/products-add", status_code=status.HTTP_201_CREATED, response_model=ProductOut)
# async def add_product(data: ProductIn, db=Depends(get_db), admin=Depends(CurrentAdmin)):
#     doc = data.model_dump()
#     doc["created_at"] = datetime.utcnow()  # ← افزودن زمان ساخت
#     res = await db.products.insert_one(doc)
#     doc["_id"] = str(res.inserted_id)
#     await publish_event("product.created", {"product_id": doc["_id"], "admin_id": admin["id"]})
#     return ProductOut(**doc)

# @router.delete("/products-delete/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_product(product_id: str, db=Depends(get_db), admin=Depends(CurrentAdmin)):
#     res = await db.products.delete_one({"_id": ObjectId(product_id)})
#     if res.deleted_count == 0:
#         raise HTTPException(404, "Product not found")
#     await publish_event("product.deleted", {"product_id": product_id, "admin_id": admin["id"]})

# # ---------- کاربران ----------

# @router.delete("/users-delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_user(user_id: int, admin=Depends(CurrentAdmin)):
#     from app.iam import iam_pb2
#     try:
#         await stub.DeleteUser(iam_pb2.DeleteUserRequest(user_id=user_id))
#     except Exception:
#         raise HTTPException(502, "IAM gRPC unavailable")
#     await publish_event("user.deleted", {"user_id": user_id, "admin_id": admin["id"]})

# @router.patch("/ban-users/{user_id}", status_code=status.HTTP_200_OK)
# async def ban_user(user_id: int, admin=Depends(CurrentAdmin)):
#     from app.iam import iam_pb2
#     try:
#         await stub.BanUser(iam_pb2.BanUserRequest(user_id=user_id))
#     except Exception:
#         raise HTTPException(502, "IAM gRPC unavailable")
#     await publish_event("user.banned", {"user_id": user_id, "admin_id": admin["id"]})
#     return {"detail": "user banned"}


# @router.post("/add-categories", status_code=status.HTTP_201_CREATED)
# async def add_category(data: CategoryIn, db=Depends(get_db), admin=Depends(CurrentAdmin)):
#     doc = data.model_dump()
#     res = await db.category.insert_one(doc)
#     doc["_id"] = str(res.inserted_id)
#     await publish_event("category.created", {"category_id": doc["_id"], "admin_id": admin["id"]})
#     return doc
