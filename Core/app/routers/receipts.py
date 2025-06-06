# app/routers/receipts.py
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime, timedelta
from decimal import Decimal
from app.schemas import ReceiptOut, BasketItem
from app.deps import get_db, CurrentUser
from app.routers._utils import fix_objectid

router = APIRouter(prefix="/receipts", tags=["receipts"])

# مشاهدهٔ فاکتورهای کاربر
@router.get("/", response_model=list[ReceiptOut])
async def visit_receipts(db=Depends(get_db), user=Depends(CurrentUser)):
    cursor = db.receipts.find({"user_id": user["id"]}).sort("created_at", -1)
    result = []
    async for doc in cursor:
        result.append(fix_objectid(doc))
    return result

# مشاهدهٔ جزئیات یک فاکتور خاص
@router.get("/{receipt_id}", response_model=ReceiptOut)
async def get_receipt(receipt_id: str, db=Depends(get_db), user=Depends(CurrentUser)):
    doc = await db.receipts.find_one({"_id": ObjectId(receipt_id), "user_id": user["id"]})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Receipt not found")
    return fix_objectid(doc)
