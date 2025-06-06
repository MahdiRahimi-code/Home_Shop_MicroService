# app/routers/products.py
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.deps import get_db
from app.schemas import ProductOut
from app.routers._utils import fix_objectid

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}", response_model=ProductOut)
async def visit_product(product_id: str, db=Depends(get_db)):
    doc = await db.products.find_one({"_id": ObjectId(product_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    doc = fix_objectid(doc)
    return doc


@router.get("/", response_model=list[ProductOut])
async def list_products(category_id: str | None = None, db=Depends(get_db)):
    query = {"category_id": category_id} if category_id else {}
    cursor = db.products.find(query).sort("created_at", -1)
    result = []
    async for doc in cursor:
        result.append(fix_objectid(doc))
    return result



# app/routers/products.py (اضافه انتهای فایل)

from app.schemas import ReviewOut

@router.get("/{product_id}/reviews", response_model=list[ReviewOut])
async def list_product_reviews(product_id: str, db=Depends(get_db)):
    cursor = db.reviews.find({"product_id": ObjectId(product_id)}).sort("created_at", -1)
    result = []
    async for doc in cursor:
        result.append(fix_objectid(doc))
    return result







# from fastapi import APIRouter, Depends, HTTPException, status
# from bson import ObjectId
# from app.deps import get_db
# from app.schemas import ProductOut
# from bson import ObjectId
# from app.schemas import ProductOut


# router = APIRouter(prefix="/products", tags=["products"])


# @router.get("/{product_id}", response_model=ProductOut)
# async def visit_product(product_id: str, db=Depends(get_db)):
#     doc = await db.products.find_one({"_id": ObjectId(product_id)})
#     if not doc:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
#     doc["_id"] = str(doc["_id"])
#     return doc

#-------------------------------------------

# from fastapi import APIRouter, Depends, HTTPException, status
# from bson import ObjectId
# from app.schemas import ProductOut
# from app.deps import get_db, CurrentUser

# router = APIRouter(prefix="/products", tags=["products"])

# @router.get("/{product_id}", response_model=ProductOut)
# async def visit_product(product_id: str, db=Depends(get_db)):
#     doc = await db.products.find_one({"_id": ObjectId(product_id)})
#     if not doc:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
#     return doc

# @router.get("/", response_model=list[ProductOut])
# async def list_products(category_id: str | None = None, db=Depends(get_db)):
#     query = {"category_id": category_id} if category_id else {}
#     cursor = db.products.find(query).sort("created_at", -1)
#     return [doc async for doc in cursor]
