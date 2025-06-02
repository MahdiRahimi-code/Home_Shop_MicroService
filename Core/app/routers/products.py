from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from app.deps import get_db
from app.schemas import ProductOut
from bson import ObjectId
from app.schemas import ProductOut


router = APIRouter(prefix="/products", tags=["products"])


@router.get("/{product_id}", response_model=ProductOut)
async def visit_product(product_id: str, db=Depends(get_db)):
    doc = await db.products.find_one({"_id": ObjectId(product_id)})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    doc["_id"] = str(doc["_id"])
    return doc



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
