from fastapi import APIRouter, Depends
from fastapi import status, HTTPException
from datetime import datetime, timedelta
from app.schemas import PaymentOut
from app.deps import get_db, CurrentUser

router = APIRouter(prefix="/payments", tags=["payments"])

@router.get("/history", response_model=list[PaymentOut])
async def visit_previous_payments(db=Depends(get_db), user=Depends(CurrentUser)):
    cursor = db.payments.find({"user_id": user["id"], "status": "paid"}).sort("created_at", -1)
    result = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  
        result.append(doc)
    return result


@router.get("/upcoming", response_model=list[PaymentOut])
async def visit_upcoming_payments(db=Depends(get_db), user=Depends(CurrentUser)):
    cursor = db.payments.find({
        "user_id": user["id"],
        "status": "pending",
        "estimated_settlement": {"$gte": datetime.utcnow()}
    })
    return [doc async for doc in cursor]

@router.post("/do-payment", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
async def do_payment(amount: float, db=Depends(get_db), user=Depends(CurrentUser)):
    doc = {
        "user_id": user["id"],
        "amount": amount,
        "status": "paid",
        "created_at": datetime.utcnow(),
        "estimated_settlement": datetime.utcnow() + timedelta(days=0)
    }
    res = await db.payments.insert_one(doc)
    doc["_id"] = str(res.inserted_id)  # ← این خط ضروریه
    return doc

