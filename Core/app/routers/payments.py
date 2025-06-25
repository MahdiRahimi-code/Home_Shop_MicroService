# app/routers/payments.py

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime, timedelta
from decimal import Decimal
from app.schemas import BasketItem, ReceiptOut
from app.deps import get_db, CurrentUser
from app.routers._utils import fix_objectid

router = APIRouter(prefix="/payments", tags=["payments"])


async def _calculate_total_with_discount(db, items: list[BasketItem]) -> Decimal:
    total = Decimal("0")
    now = datetime.utcnow()
    for it in items:
        prod = await db.products.find_one({
            "_id": ObjectId(it.product_id),
            "is_active": True
        })
        if not prod:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {it.product_id} not found or inactive"
            )
        price = Decimal(str(prod["price"]))
        disc_id = prod.get("discount_id")
        if disc_id:
            disc = await db.discounts.find_one({"_id": ObjectId(disc_id)})
            if disc and disc.get("is_active", False):
                exp = disc.get("expiration_date")
                if exp and exp <= now:
                    # expire it
                    await db.discounts.update_one(
                        {"_id": ObjectId(disc_id)},
                        {"$set": {"is_active": False}}
                    )
                else:
                    pct = Decimal(str(disc["percentage"]))
                    price *= (Decimal("1") - pct / Decimal("100"))
        total += price * it.quantity
    return total



# app/routers/payments.py

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime, timedelta
from decimal import Decimal
from app.schemas import BasketItem, ReceiptOut
from app.deps import get_db, CurrentUser
from app.routers._utils import fix_objectid

router = APIRouter(prefix="/payments", tags=["payments"])

# … _calculate_total_with_discount as before …

@router.post("/pay-basket", response_model=ReceiptOut, status_code=status.HTTP_201_CREATED)
async def pay_basket(db=Depends(get_db), user=Depends(CurrentUser)):
    # Load basket
    basket = await db.baskets.find_one({"user_id": user["id"]})
    if not basket or not basket.get("items"):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Basket is empty")

    # Build BasketItem list
    items = [
        BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"])
        for it in basket["items"]
    ]

    # 1) STOCK CHECK: ensure enough inventory for each item
    for it in items:
        prod = await db.products.find_one({"_id": ObjectId(it.product_id)})
        if not prod or prod["stock_num"] < it.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for product {it.product_id}"
            )

    # 2) Recalculate total (with discounts)
    total_price = await _calculate_total_with_discount(db, items)

    # 3) Wallet check & deduct
    wallet = await db.wallets.find_one({"user_id": user["id"]})
    if not wallet or Decimal(str(wallet["balance"])) < total_price:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Insufficient wallet balance")
    new_bal = Decimal(str(wallet["balance"])) - total_price
    await db.wallets.update_one(
        {"_id": wallet["_id"]},
        {"$set": {"balance": float(new_bal)}}
    )

    # 4) Default address lookup
    addr = await db.addresses.find_one({
        "user_id": user["id"],
        "is_default": True
    })
    if not addr:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No default address set for user")

    # 5) Create receipt
    now = datetime.utcnow()
    est = now + timedelta(days=5)
    receipt = {
        "user_id": user["id"],
        "items": basket["items"],
        "total_price": float(total_price),
        "address_id": addr["_id"],
        "created_at": now,
        "estimated_delivery": est,
        "status": "paid"
    }
    res = await db.receipts.insert_one(receipt)
    receipt["_id"] = res.inserted_id

    # 6) DECREMENT STOCK
    for it in items:
        await db.products.update_one(
            {"_id": ObjectId(it.product_id)},
            {"$inc": {"stock_num": -it.quantity}}
        )

    # 7) Record payment entry
    await db.payments.insert_one({
        "user_id": user["id"],
        "amount": float(total_price),
        "status": "paid",
        "created_at": now,
        "estimated_settlement": est
    })

    # 8) Clear basket
    await db.baskets.delete_one({"user_id": user["id"]})

    # 9) Prepare output
    out = fix_objectid(receipt)
    out["items"] = [
        {"product_id": str(it["product_id"]), "quantity": it["quantity"]}
        for it in receipt["items"]
    ]
    out["address_id"] = str(out["address_id"])
    return out




# @router.post("/pay-basket", response_model=ReceiptOut, status_code=status.HTTP_201_CREATED)
# async def pay_basket(db=Depends(get_db), user=Depends(CurrentUser)):
#     basket = await db.baskets.find_one({"user_id": user["id"]})
#     if not basket or not basket.get("items"):
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Basket is empty"
#         )

#     items = [
#         BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"])
#         for it in basket["items"]
#     ]
#     total_price = await _calculate_total_with_discount(db, items)

#     # Wallet
#     wallet = await db.wallets.find_one({"user_id": user["id"]})
#     if not wallet or Decimal(str(wallet["balance"])) < total_price:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Insufficient wallet balance"
#         )
#     new_bal = Decimal(str(wallet["balance"])) - total_price
#     await db.wallets.update_one(
#         {"_id": wallet["_id"]},
#         {"$set": {"balance": float(new_bal)}}
#     )

#     # Default address
#     addr = await db.addresses.find_one({
#         "user_id": user["id"],
#         "is_default": True
#     })
#     if not addr:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="No default address set for user"
#         )

#     now = datetime.utcnow()
#     est = now + timedelta(days=5)
#     receipt = {
#         "user_id": user["id"],
#         "items": basket["items"],
#         "total_price": float(total_price),
#         "address_id": addr["_id"],
#         "created_at": now,
#         "estimated_delivery": est,
#         "status": "paid"
#     }
#     res = await db.receipts.insert_one(receipt)
#     receipt["_id"] = res.inserted_id

#     payment_doc = {
#         "user_id": user["id"],
#         "amount": float(total_price),
#         "status": "paid",
#         "created_at": now,
#         "estimated_settlement": est
#     }
#     await db.payments.insert_one(payment_doc)
#     # ————————————————————————————————

#     await db.baskets.delete_one({"user_id": user["id"]})

#     out = fix_objectid(receipt)
#     out["items"] = [
#         {"product_id": str(it["product_id"]), "quantity": it["quantity"]}
#         for it in receipt["items"]
#     ]
#     out["address_id"] = str(out["address_id"])
#     return out



# from fastapi import APIRouter, Depends, status, HTTPException
# from datetime import datetime, timedelta
# from app.schemas import PaymentOut
# from app.deps import get_db, CurrentUser
# from app.routers._utils import fix_objectid
# from fastapi import APIRouter, Depends, HTTPException, status
# from bson import ObjectId
# from decimal import Decimal
# from app.schemas import PaymentOut, BasketItem, ReceiptOut



# router = APIRouter(prefix="/payments", tags=["payments"])


# @router.get("/history", response_model=list[PaymentOut])
# async def visit_previous_payments(db=Depends(get_db), user=Depends(CurrentUser)):
#     cursor = db.payments.find({"user_id": user["id"], "status": "paid"}).sort("created_at", -1)
#     result = []
#     async for doc in cursor:
#         result.append(fix_objectid(doc))
#     return result


# @router.get("/upcoming", response_model=list[PaymentOut])
# async def visit_upcoming_payments(db=Depends(get_db), user=Depends(CurrentUser)):
#     cursor = db.payments.find({
#         "user_id": user["id"],
#         "status": "pending",
#         "estimated_settlement": {"$gte": datetime.utcnow()}
#     })
#     result = []
#     async for doc in cursor:
#         result.append(fix_objectid(doc))
#     return result


# # @router.post("/pay-basket", response_model=ReceiptOut, status_code=status.HTTP_201_CREATED)
# # async def pay_basket(address_id: str, db=Depends(get_db), user=Depends(CurrentUser)):
# #     basket = await db.baskets.find_one({"user_id": user["id"]})
# #     if not basket or not basket.get("items"):
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Basket is empty")

# #     items = [BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"]) for it in basket["items"]]

# #     total_price = Decimal(str(basket["total_price"]))

# #     wallet = await db.wallets.find_one({"user_id": user["id"]})
# #     if not wallet or Decimal(str(wallet["balance"])) < total_price:
# #         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient wallet balance")

# #     new_balance = Decimal(str(wallet["balance"])) - total_price
# #     wallet["balance"] = float(new_balance)
# #     await db.wallets.replace_one({"_id": wallet["_id"]}, wallet)

# #     now = datetime.utcnow()
# #     estimated = now + timedelta(days=5)
# #     addr = await db.addresses.find_one({"_id": ObjectId(address_id), "user_id": user["id"]})
# #     if not addr:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

# #     receipt = {
# #         "user_id": user["id"],
# #         "items": [
# #             {"product_id": item["product_id"], "quantity": item["quantity"]}
# #             for item in basket["items"]
# #         ],
# #         "total_price": float(total_price),
# #         "address_id": ObjectId(address_id),
# #         "created_at": now,
# #         "estimated_delivery": estimated,
# #         "status": "paid"
# #     }
# #     res = await db.receipts.insert_one(receipt)
# #     receipt["_id"] = res.inserted_id

# #     await db.baskets.delete_one({"user_id": user["id"]})

# #     receipt = fix_objectid(receipt)
# #     receipt["items"] = [
# #         {"product_id": str(it["product_id"]), "quantity": it["quantity"]}
# #         for it in receipt["items"]
# #     ]
# #     receipt["address_id"] = str(receipt["address_id"])
# #     return receipt



# async def _calculate_total_with_discount(db, items: list[BasketItem]) -> Decimal:
#     total = Decimal("0")
#     now = datetime.utcnow()
#     for it in items:
#         prod = await db.products.find_one({"_id": ObjectId(it.product_id), "is_active": True})
#         if not prod:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#                                 detail=f"Product {it.product_id} not found or inactive")
#         price = Decimal(str(prod["price"]))
#         # apply discount if any
#         disc_id = prod.get("discount_id")
#         if disc_id:
#             disc = await db.discounts.find_one({"_id": ObjectId(disc_id)})
#             if disc and disc.get("is_active", False):
#                 exp = disc.get("expiration_date")
#                 if exp and exp <= now:
#                     # deactivate expired discount
#                     await db.discounts.update_one(
#                         {"_id": ObjectId(disc_id)},
#                         {"$set": {"is_active": False}}
#                     )
#                 else:
#                     pct = Decimal(str(disc["percentage"]))
#                     price = price * (Decimal("1") - pct / Decimal("100"))
#         total += price * it.quantity
#     return total


# # @router.post("/pay-basket", response_model=ReceiptOut, status_code=status.HTTP_201_CREATED)
# # async def pay_basket(address_id: str, db=Depends(get_db), user=Depends(CurrentUser)):
# @router.post("/pay-basket", response_model=ReceiptOut, status_code=status.HTTP_201_CREATED)
# async def pay_basket(db=Depends(get_db), user=Depends(CurrentUser)):
#     # 1. load basket
#     basket = await db.baskets.find_one({"user_id": user["id"]})
#     if not basket or not basket.get("items"):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Basket is empty")

#     # 2. build BasketItem list
#     items = [
#         BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"])
#         for it in basket["items"]
#     ]

#     # 3. recalc total with discounts
#     total_price = await _calculate_total_with_discount(db, items)

#     # 4. wallet check & deduct
#     wallet = await db.wallets.find_one({"user_id": user["id"]})
#     if not wallet or Decimal(str(wallet["balance"])) < total_price:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                             detail="Insufficient wallet balance")
#     new_bal = Decimal(str(wallet["balance"])) - total_price
#     await db.wallets.update_one(
#         {"_id": wallet["_id"]},
#         {"$set": {"balance": float(new_bal)}}
#     )

#     # 5. verify address
#     # addr = await db.addresses.find_one(
#     #     {"_id": ObjectId(address_id), "user_id": user["id"]}
#     # )
#     # if not addr:
#     #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
#     #                         detail="Address not found")

#     # 5. load default address for this user
#     addr = await db.addresses.find_one({
#         "user_id": user["id"],
#         "is_default": True
#     })
#     if not addr:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="No default address set for user"
#         )

#     # 6. create receipt
#     now = datetime.utcnow()
#     est = now + timedelta(days=5)
#     receipt = {
#         "user_id": user["id"],
#         "items": basket["items"],  # list of dicts {product_id, quantity}
#         "total_price": float(total_price),
#         # "address_id": ObjectId(address_id),
#         "address_id": addr["_id"],
#         "created_at": now,
#         "estimated_delivery": est,
#         "status": "paid"
#     }
#     res = await db.receipts.insert_one(receipt)
#     receipt["_id"] = res.inserted_id

#     # 7. clear basket
#     await db.baskets.delete_one({"user_id": user["id"]})

#     # 8. prepare output
#     receipt = fix_objectid(receipt)
#     receipt["items"] = [
#         {"product_id": str(it["product_id"]), "quantity": it["quantity"]}
#         for it in receipt["items"]
#     ]
#     receipt["address_id"] = str(receipt["address_id"])
#     return receipt








# # @router.post("/do-payment", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
# # async def do_payment(amount: float, db=Depends(get_db), user=Depends(CurrentUser)):
# #     doc = {
# #         "user_id": user["id"],
# #         "amount": amount,
# #         "status": "paid",
# #         "created_at": datetime.utcnow(),
# #         "estimated_settlement": datetime.utcnow() + timedelta(days=0)
# #     }
# #     res = await db.payments.insert_one(doc)
# #     doc["_id"] = res.inserted_id
# #     return fix_objectid(doc)



# # from fastapi import APIRouter, Depends
# # from fastapi import status, HTTPException
# # from datetime import datetime, timedelta
# # from app.schemas import PaymentOut
# # from app.deps import get_db, CurrentUser

# # router = APIRouter(prefix="/payments", tags=["payments"])

# # @router.get("/history", response_model=list[PaymentOut])
# # async def visit_previous_payments(db=Depends(get_db), user=Depends(CurrentUser)):
# #     cursor = db.payments.find({"user_id": user["id"], "status": "paid"}).sort("created_at", -1)
# #     result = []
# #     async for doc in cursor:
# #         doc["_id"] = str(doc["_id"])  
# #         result.append(doc)
# #     return result


# # @router.get("/upcoming", response_model=list[PaymentOut])
# # async def visit_upcoming_payments(db=Depends(get_db), user=Depends(CurrentUser)):
# #     cursor = db.payments.find({
# #         "user_id": user["id"],
# #         "status": "pending",
# #         "estimated_settlement": {"$gte": datetime.utcnow()}
# #     })
# #     return [doc async for doc in cursor]

# # @router.post("/do-payment", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
# # async def do_payment(amount: float, db=Depends(get_db), user=Depends(CurrentUser)):
# #     doc = {
# #         "user_id": user["id"],
# #         "amount": amount,
# #         "status": "paid",
# #         "created_at": datetime.utcnow(),
# #         "estimated_settlement": datetime.utcnow() + timedelta(days=0)
# #     }
# #     res = await db.payments.insert_one(doc)
# #     doc["_id"] = str(res.inserted_id)
# #     return doc

