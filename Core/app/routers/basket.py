# app/routers/basket.py

from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime
from decimal import Decimal
from app.schemas import BasketItem, BasketOut
from app.deps import get_db, CurrentUser
from app.routers._utils import fix_objectid

router = APIRouter(prefix="/basket", tags=["basket"])


async def _calculate_total(db, items: list[BasketItem]) -> Decimal:
    total = Decimal("0")
    for it in items:
        prod = await db.products.find_one({"_id": ObjectId(it.product_id)})
        if not prod:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product {it.product_id} not found"
            )
        price = Decimal(str(prod["price"]))
        total += price * it.quantity
    return total


@router.get("/", response_model=BasketOut)
async def visit_basket(db=Depends(get_db), user=Depends(CurrentUser)):
    basket = await db.baskets.find_one({"user_id": user["id"]})
    if not basket or not basket.get("items"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your basket is empty"
        )

    out = fix_objectid(basket)
    out["items"] = [
        {"product_id": str(item["product_id"]), "quantity": item["quantity"]}
        for item in basket["items"]
    ]
    return out


@router.post("/add", response_model=BasketOut, status_code=status.HTTP_200_OK)
async def add_product_to_basket(
    data: BasketItem,
    db=Depends(get_db),
    user=Depends(CurrentUser)
):
    prod = await db.products.find_one({
        "_id": ObjectId(data.product_id),
        "is_active": True
    })
    if not prod:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or inactive"
        )
    if prod["stock_num"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product out of stock"
        )

    basket = await db.baskets.find_one({"user_id": user["id"]})
    if not basket:
        new_basket = {
            "user_id": user["id"],
            "items": [
                {"product_id": ObjectId(data.product_id), "quantity": data.quantity}
            ],
            "created_at": datetime.utcnow()
        }
        total = await _calculate_total(db, [data])
        new_basket["total_price"] = float(total)
        res = await db.baskets.insert_one(new_basket)
        new_basket["_id"] = res.inserted_id

        out = fix_objectid(new_basket)
        out["items"] = [
            {"product_id": str(item["product_id"]), "quantity": item["quantity"]}
            for item in new_basket["items"]
        ]
        return out

    # update existing basket
    items = basket["items"]
    for item in items:
        if str(item["product_id"]) == data.product_id:
            item["quantity"] += data.quantity
            if item["quantity"] <= 0:
                items.remove(item)
            break
    else:
        if data.quantity > 0:
            items.append({
                "product_id": ObjectId(data.product_id),
                "quantity": data.quantity
            })

    if not items:
        await db.baskets.delete_one({"user_id": user["id"]})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your basket is now empty"
        )

    basket["items"] = items
    total = await _calculate_total(
        db,
        [BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"])
         for it in items]
    )
    basket["total_price"] = float(total)
    basket["updated_at"] = datetime.utcnow()
    await db.baskets.replace_one({"_id": basket["_id"]}, basket)

    out = fix_objectid(basket)
    out["items"] = [
        {"product_id": str(it["product_id"]), "quantity": it["quantity"]}
        for it in items
    ]
    return out


@router.delete("/remove/{product_id}", status_code=status.HTTP_200_OK)
async def remove_product_from_basket(
    product_id: str,
    db=Depends(get_db),
    user=Depends(CurrentUser)
):
    basket = await db.baskets.find_one({"user_id": user["id"]})
    if not basket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Basket not found"
        )
    items = [
        it for it in basket["items"]
        if str(it["product_id"]) != product_id
    ]
    if len(items) == len(basket["items"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not in basket"
        )
    if not items:
        await db.baskets.delete_one({"user_id": user["id"]})
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your basket is now empty"
        )

    basket["items"] = items
    total = await _calculate_total(
        db,
        [BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"])
         for it in items]
    )
    basket["total_price"] = float(total)
    basket["updated_at"] = datetime.utcnow()
    await db.baskets.replace_one({"_id": basket["_id"]}, basket)

    # out = fix_objectid(basket)
    # out["items"] = [
    #     {"product_id": str(it["product_id"]), "quantity": it["quantity"]}
    #     for it in items
    # ]
    # return out

    basket["_id"] = str(basket["_id"])

    # اگر address_id یا discount_id هست و ObjectId باشه، تبدیلش کن
    if basket.get("address_id"):
        basket["address_id"] = str(basket["address_id"])
    if basket.get("discount_id"):
        basket["discount_id"] = str(basket["discount_id"])

    # آیتم‌ها
    basket["items"] = [
        {"product_id": str(it["product_id"]), "quantity": it["quantity"]}
        for it in items
    ]

    return basket




# from fastapi import APIRouter, Depends, HTTPException, status
# from bson import ObjectId
# from datetime import datetime
# from decimal import Decimal
# from app.schemas import BasketItem, BasketOut
# from app.deps import get_db, CurrentUser
# from app.routers._utils import fix_objectid

# router = APIRouter(prefix="/basket", tags=["basket"])

# async def _calculate_total(db, items: list[BasketItem]) -> Decimal:
#     """
#     یک تابع کمکی برای محاسبهٔ مبلغ کلِ اقلامِ سبد:
#     مجموعِ price * quantity برای هر آیتم.
#     """
#     total = Decimal("0")
#     for it in items:
#         prod = await db.products.find_one({"_id": ObjectId(it.product_id)})
#         if not prod:
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {it.product_id} not found")
#         price = Decimal(str(prod["price"]))
#         total += price * it.quantity
#     return total

# # بازدید از سبد فعلی کاربر
# @router.get("/", response_model=BasketOut)
# async def visit_basket(db=Depends(get_db), user=Depends(CurrentUser)):
#     basket = await db.baskets.find_one({"user_id": user["id"]})
#     # اگر هیچ آیتمی در سبد نیست، خطای 404 بده
#     if not basket or not basket.get("items"):
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Your basket is empty"
#         )
#     # basket = await db.baskets.find_one({"user_id": user["id"]})
#     # if not basket:
#     #     # اگر سبد وجود ندارد، یک سبد خالی برمی‌گردانیم
#     #     return BasketOut(
#     #         id="",
#     #         user_id=user["id"],
#     #         items=[],
#     #         total_price=Decimal("0"),
#     #         created_at=datetime.utcnow()
#     #     )
#     # تبدیل ObjectId و آماده‌سازی برای خروجی
#     # basket = fix_objectid(basket)
#     # # در قالب مدلِ BasketOut
#     # return basket
#     # اول، تمام ObjectIdهای اصلی را به str تبدیل کنیم
#     out = fix_objectid(basket)
#     # بعد، nested items[*].product_id هم باید str بشود
#     out["items"] = [
#         {"product_id": str(item["product_id"]), "quantity": item["quantity"]}
#         for item in basket["items"]
#     ]
#     return out


# @router.post("/add", response_model=BasketOut, status_code=status.HTTP_200_OK)
# async def add_product_to_basket(data: BasketItem, db=Depends(get_db), user=Depends(CurrentUser)):
#     # ابتدا کالای ورودی باید وجود داشته باشد
#     prod = await db.products.find_one({"_id": ObjectId(data.product_id), "is_active": True})
#     if not prod:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

#     if prod["stock_num"] <= 0:
#         raise HTTPException(status.HTTP_400_BAD_REQUEST, "Product out of stock")

#     basket = await db.baskets.find_one({"user_id": user["id"]})
#     if not basket:
#         # اگر سبد وجود ندارد، بسازیم
#         new_basket = {
#             "user_id": user["id"],
#             "items": [
#                 {"product_id": ObjectId(data.product_id), "quantity": data.quantity}
#             ],
#             "created_at": datetime.utcnow()
#         }
#         total = await _calculate_total(db, [data])
#         new_basket["total_price"] = float(total)
#         res = await db.baskets.insert_one(new_basket)
#         new_basket["_id"] = res.inserted_id
#         # return fix_objectid(new_basket)
#         # deep‐convert everything before returning
#         out = fix_objectid(new_basket)
#         out["items"] = [
#             {"product_id": str(item["product_id"]), "quantity": item["quantity"]}
#             for item in new_basket["items"]
#         ]
#         return out

#     # اگر سبد هست، ببینیم آیا آن کالا قبلاً وجود دارد؟
#     updated_items = basket["items"]
#     found = False
#     for item in updated_items:
#         if str(item["product_id"]) == data.product_id:
#             item["quantity"] += data.quantity
#             if item["quantity"] <= 0:
#                 # اگر تعداد زیر یا مساوی صفر شد، از لیست حذف می‌کنیم
#                 updated_items.remove(item)
#             found = True
#             break

#     if not found and data.quantity > 0:
#         updated_items.append({"product_id": ObjectId(data.product_id), "quantity": data.quantity})

#     # اگر لیست آیتم‌ها خالی شد، حذفِ کل سبد هم می‌تواند منطقی باشد؛ اما اینجا فقط خالی‌اش می‌کنیم
#     if not updated_items:
#         await db.baskets.delete_one({"user_id": user["id"]})
#         return {"detail": "Basket is now empty"}

#     # مجدد محاسبهٔ total_price
#     basket["items"] = updated_items
#     total = await _calculate_total(db, [BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"]) for it in updated_items])
#     basket["total_price"] = float(total)
#     basket["updated_at"] = datetime.utcnow()
#     # await db.baskets.replace_one({"_id": basket["_id"]}, basket)
#     # return fix_objectid(basket)
#     await db.baskets.replace_one({"_id": basket["_id"]}, basket)
#     out = fix_objectid(basket)
#     out["items"] = [
#         {"product_id": str(item["product_id"]), "quantity": item["quantity"]}
#         for item in updated_items
#     ]
#     return out




# # # اضافه کردن یا اصلاح یک آیتم (quantity) در سبد
# # @router.post("/add", status_code=status.HTTP_200_OK)
# # async def add_product_to_basket(data: BasketItem, db=Depends(get_db), user=Depends(CurrentUser)):
# #     # ابتدا کالای ورودی باید وجود داشته باشد
# #     prod = await db.products.find_one({"_id": ObjectId(data.product_id), "is_active": True})
# #     if not prod:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

# #     if prod["stock_num"] <= 0:
# #         raise HTTPException(status.HTTP_400_BAD_REQUEST, "Product out of stock")

# #     basket = await db.baskets.find_one({"user_id": user["id"]})
# #     if not basket:
# #         # اگر سبد وجود ندارد، بسازیم
# #         new_basket = {
# #             "user_id": user["id"],
# #             "items": [
# #                 {"product_id": ObjectId(data.product_id), "quantity": data.quantity}
# #             ],
# #             "created_at": datetime.utcnow()
# #         }
# #         total = await _calculate_total(db, [data])
# #         new_basket["total_price"] = float(total)
# #         res = await db.baskets.insert_one(new_basket)
# #         new_basket["_id"] = res.inserted_id
# #         return fix_objectid(new_basket)

# #     # اگر سبد هست، ببینیم آیا آن کالا قبلاً وجود دارد؟
# #     updated_items = basket["items"]
# #     found = False
# #     for item in updated_items:
# #         if str(item["product_id"]) == data.product_id:
# #             item["quantity"] += data.quantity
# #             if item["quantity"] <= 0:
# #                 # اگر تعداد زیر یا مساوی صفر شد، از لیست حذف می‌کنیم
# #                 updated_items.remove(item)
# #             found = True
# #             break

# #     if not found and data.quantity > 0:
# #         updated_items.append({"product_id": ObjectId(data.product_id), "quantity": data.quantity})

# #     # اگر لیست آیتم‌ها خالی شد، حذفِ کل سبد هم می‌تواند منطقی باشد؛ اما اینجا فقط خالی‌اش می‌کنیم
# #     if not updated_items:
# #         await db.baskets.delete_one({"user_id": user["id"]})
# #         return {"detail": "Basket is now empty"}

# #     # مجدد محاسبهٔ total_price
# #     basket["items"] = updated_items
# #     total = await _calculate_total(db, [BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"]) for it in updated_items])
# #     basket["total_price"] = float(total)
# #     basket["updated_at"] = datetime.utcnow()
# #     await db.baskets.replace_one({"_id": basket["_id"]}, basket)
# #     return fix_objectid(basket)

# # حذف یک کالا کامل از سبد
# @router.delete("/remove/{product_id}", status_code=status.HTTP_200_OK)
# async def remove_product_from_basket(product_id: str, db=Depends(get_db), user=Depends(CurrentUser)):
#     basket = await db.baskets.find_one({"user_id": user["id"]})
#     if not basket:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Basket not found")
#     updated_items = [it for it in basket["items"] if str(it["product_id"]) != product_id]
#     if len(updated_items) == len(basket["items"]):
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not in basket")
#     if not updated_items:
#         await db.baskets.delete_one({"user_id": user["id"]})
#         return {"detail": "Basket is now empty"}
#     # وگرنه باز محاسبهٔ قیمت کل
#     total = await _calculate_total(db, [BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"]) for it in updated_items])
#     basket["items"] = updated_items
#     basket["total_price"] = float(total)
#     basket["updated_at"] = datetime.utcnow()
#     await db.baskets.replace_one({"_id": basket["_id"]}, basket)
#     return fix_objectid(basket)
