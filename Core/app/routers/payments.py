# app/routers/payments.py
from fastapi import APIRouter, Depends, status, HTTPException
from datetime import datetime, timedelta
from app.schemas import PaymentOut
from app.deps import get_db, CurrentUser
from app.routers._utils import fix_objectid

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/history", response_model=list[PaymentOut])
async def visit_previous_payments(db=Depends(get_db), user=Depends(CurrentUser)):
    cursor = db.payments.find({"user_id": user["id"], "status": "paid"}).sort("created_at", -1)
    result = []
    async for doc in cursor:
        result.append(fix_objectid(doc))
    return result


@router.get("/upcoming", response_model=list[PaymentOut])
async def visit_upcoming_payments(db=Depends(get_db), user=Depends(CurrentUser)):
    cursor = db.payments.find({
        "user_id": user["id"],
        "status": "pending",
        "estimated_settlement": {"$gte": datetime.utcnow()}
    })
    result = []
    async for doc in cursor:
        result.append(fix_objectid(doc))
    return result



# app/routers/payments.py
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime, timedelta
from decimal import Decimal
from app.schemas import PaymentOut, BasketItem, ReceiptOut
from app.deps import get_db, CurrentUser
from app.routers._utils import fix_objectid

router = APIRouter(prefix="/payments", tags=["payments"])

@router.post("/pay-basket", response_model=ReceiptOut, status_code=status.HTTP_201_CREATED)
async def pay_basket(address_id: str, db=Depends(get_db), user=Depends(CurrentUser)):
    """
    پرداخت کلِ سبد کاربر:
    1. ابتدا سبد کاربر (baskets) را پیدا کن
    2. اگر خالی یا وجود نداشت خطا بده
    3. موجودی کیف پول را چک کن؛ اگر کافی نبود 400 بده
    4. مبلغ را از کیف پول کم کن
    5. یک داکیومنت جدید در receipts بساز
    6. سبد را خالی کن
    7. return فاکتور
    """
    # 1. پیدا کردن سبد
    basket = await db.baskets.find_one({"user_id": user["id"]})
    if not basket or not basket.get("items"):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Basket is empty")

    # تبدیل آیتم‌ها به لیستی از BasketItem برای محاسبه
    items = [BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"]) for it in basket["items"]]

    # 2. مبلغ کل را بخوان (از داکیومنت سبد)
    total_price = Decimal(str(basket["total_price"]))

    # 3. موجودی کیف پول
    wallet = await db.wallets.find_one({"user_id": user["id"]})
    if not wallet or Decimal(str(wallet["balance"])) < total_price:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient wallet balance")

    # 4. کم کردن مبلغ از کیف پول
    new_balance = Decimal(str(wallet["balance"])) - total_price
    wallet["balance"] = float(new_balance)
    await db.wallets.replace_one({"_id": wallet["_id"]}, wallet)

    # 5. ایجاد داکیومنت فاکتور
    now = datetime.utcnow()
    estimated = now + timedelta(days=5)  # مثلاً زمان تقریبی ارسال ۵ روز بعد
    # اطمینان از این که آدرس وجود دارد
    addr = await db.addresses.find_one({"_id": ObjectId(address_id), "user_id": user["id"]})
    if not addr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    receipt = {
        "user_id": user["id"],
        "items": [
            {"product_id": item["product_id"], "quantity": item["quantity"]}
            for item in basket["items"]
        ],
        "total_price": float(total_price),
        "address_id": ObjectId(address_id),
        "created_at": now,
        "estimated_delivery": estimated,
        "status": "paid"
    }
    res = await db.receipts.insert_one(receipt)
    receipt["_id"] = res.inserted_id

    # 6. خالی کردن سبد
    await db.baskets.delete_one({"user_id": user["id"]})

    # 7. برگرداندن فاکتور با تبدیل ObjectId به str
    receipt = fix_objectid(receipt)
    receipt["items"] = [
        {"product_id": str(it["product_id"]), "quantity": it["quantity"]}
        for it in receipt["items"]
    ]
    receipt["address_id"] = str(receipt["address_id"])
    return receipt













# @router.post("/do-payment", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
# async def do_payment(amount: float, db=Depends(get_db), user=Depends(CurrentUser)):
#     doc = {
#         "user_id": user["id"],
#         "amount": amount,
#         "status": "paid",
#         "created_at": datetime.utcnow(),
#         "estimated_settlement": datetime.utcnow() + timedelta(days=0)
#     }
#     res = await db.payments.insert_one(doc)
#     doc["_id"] = res.inserted_id
#     return fix_objectid(doc)



# from fastapi import APIRouter, Depends
# from fastapi import status, HTTPException
# from datetime import datetime, timedelta
# from app.schemas import PaymentOut
# from app.deps import get_db, CurrentUser

# router = APIRouter(prefix="/payments", tags=["payments"])

# @router.get("/history", response_model=list[PaymentOut])
# async def visit_previous_payments(db=Depends(get_db), user=Depends(CurrentUser)):
#     cursor = db.payments.find({"user_id": user["id"], "status": "paid"}).sort("created_at", -1)
#     result = []
#     async for doc in cursor:
#         doc["_id"] = str(doc["_id"])  
#         result.append(doc)
#     return result


# @router.get("/upcoming", response_model=list[PaymentOut])
# async def visit_upcoming_payments(db=Depends(get_db), user=Depends(CurrentUser)):
#     cursor = db.payments.find({
#         "user_id": user["id"],
#         "status": "pending",
#         "estimated_settlement": {"$gte": datetime.utcnow()}
#     })
#     return [doc async for doc in cursor]

# @router.post("/do-payment", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
# async def do_payment(amount: float, db=Depends(get_db), user=Depends(CurrentUser)):
#     doc = {
#         "user_id": user["id"],
#         "amount": amount,
#         "status": "paid",
#         "created_at": datetime.utcnow(),
#         "estimated_settlement": datetime.utcnow() + timedelta(days=0)
#     }
#     res = await db.payments.insert_one(doc)
#     doc["_id"] = str(res.inserted_id)
#     return doc

