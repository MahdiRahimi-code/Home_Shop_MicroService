# app/routers/wallet.py
from fastapi import APIRouter, Depends, HTTPException, status
from decimal import Decimal
from app.deps import get_db, CurrentUser
from app.routers._utils import fix_objectid

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.get("/", response_model=dict)  # فقط نشانِ موجودی کیف پول
async def get_wallet(db=Depends(get_db), user=Depends(CurrentUser)):
    wallet = await db.wallets.find_one({"user_id": user["id"]})
    if not wallet:
        # اگر کیف پول وجود ندارد، با موجودی صفر برمی‌گردانیم
        return {"user_id": user["id"], "balance": 0.0}
    # تبدیل ObjectId در صورت وجود (اینجا هیچ _id‌ لازم نیست Return شود)
    return {"user_id": wallet["user_id"], "balance": wallet["balance"]}

@router.post("/deposit", status_code=status.HTTP_200_OK)
async def deposit_to_wallet(amount: float, db=Depends(get_db), user=Depends(CurrentUser)):
    if amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Amount must be positive")
    wallet = await db.wallets.find_one({"user_id": user["id"]})
    if not wallet:
        new_wallet = {"user_id": user["id"], "balance": float(Decimal(str(amount)))}
        await db.wallets.insert_one(new_wallet)
        return {"user_id": user["id"], "balance": new_wallet["balance"]}
    new_balance = Decimal(str(wallet["balance"])) + Decimal(str(amount))
    wallet["balance"] = float(new_balance)
    await db.wallets.replace_one({"_id": wallet["_id"]}, wallet)
    return {"user_id": user["id"], "balance": wallet["balance"]}
