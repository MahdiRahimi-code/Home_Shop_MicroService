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
    """
    یک تابع کمکی برای محاسبهٔ مبلغ کلِ اقلامِ سبد:
    مجموعِ price * quantity برای هر آیتم.
    """
    total = Decimal("0")
    for it in items:
        prod = await db.products.find_one({"_id": ObjectId(it.product_id)})
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product {it.product_id} not found")
        price = Decimal(str(prod["price"]))
        total += price * it.quantity
    return total

# بازدید از سبد فعلی کاربر
@router.get("/", response_model=BasketOut)
async def visit_basket(db=Depends(get_db), user=Depends(CurrentUser)):
    basket = await db.baskets.find_one({"user_id": user["id"]})
    if not basket:
        # اگر سبد وجود ندارد، یک سبد خالی برمی‌گردانیم
        return BasketOut(
            id="",
            user_id=user["id"],
            items=[],
            total_price=Decimal("0"),
            created_at=datetime.utcnow()
        )
    # تبدیل ObjectId و آماده‌سازی برای خروجی
    basket = fix_objectid(basket)
    # در قالب مدلِ BasketOut
    return basket

# اضافه کردن یا اصلاح یک آیتم (quantity) در سبد
@router.post("/add", status_code=status.HTTP_200_OK)
async def add_product_to_basket(data: BasketItem, db=Depends(get_db), user=Depends(CurrentUser)):
    # ابتدا کالای ورودی باید وجود داشته باشد
    prod = await db.products.find_one({"_id": ObjectId(data.product_id), "is_active": True})
    if not prod:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found or inactive")

    if prod["stock_num"] <= 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Product out of stock")

    basket = await db.baskets.find_one({"user_id": user["id"]})
    if not basket:
        # اگر سبد وجود ندارد، بسازیم
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
        return fix_objectid(new_basket)

    # اگر سبد هست، ببینیم آیا آن کالا قبلاً وجود دارد؟
    updated_items = basket["items"]
    found = False
    for item in updated_items:
        if str(item["product_id"]) == data.product_id:
            item["quantity"] += data.quantity
            if item["quantity"] <= 0:
                # اگر تعداد زیر یا مساوی صفر شد، از لیست حذف می‌کنیم
                updated_items.remove(item)
            found = True
            break

    if not found and data.quantity > 0:
        updated_items.append({"product_id": ObjectId(data.product_id), "quantity": data.quantity})

    # اگر لیست آیتم‌ها خالی شد، حذفِ کل سبد هم می‌تواند منطقی باشد؛ اما اینجا فقط خالی‌اش می‌کنیم
    if not updated_items:
        await db.baskets.delete_one({"user_id": user["id"]})
        return {"detail": "Basket is now empty"}

    # مجدد محاسبهٔ total_price
    basket["items"] = updated_items
    total = await _calculate_total(db, [BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"]) for it in updated_items])
    basket["total_price"] = float(total)
    basket["updated_at"] = datetime.utcnow()
    await db.baskets.replace_one({"_id": basket["_id"]}, basket)
    return fix_objectid(basket)

# حذف یک کالا کامل از سبد
@router.delete("/remove/{product_id}", status_code=status.HTTP_200_OK)
async def remove_product_from_basket(product_id: str, db=Depends(get_db), user=Depends(CurrentUser)):
    basket = await db.baskets.find_one({"user_id": user["id"]})
    if not basket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Basket not found")
    updated_items = [it for it in basket["items"] if str(it["product_id"]) != product_id]
    if len(updated_items) == len(basket["items"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not in basket")
    if not updated_items:
        await db.baskets.delete_one({"user_id": user["id"]})
        return {"detail": "Basket is now empty"}
    # وگرنه باز محاسبهٔ قیمت کل
    total = await _calculate_total(db, [BasketItem(product_id=str(it["product_id"]), quantity=it["quantity"]) for it in updated_items])
    basket["items"] = updated_items
    basket["total_price"] = float(total)
    basket["updated_at"] = datetime.utcnow()
    await db.baskets.replace_one({"_id": basket["_id"]}, basket)
    return fix_objectid(basket)
