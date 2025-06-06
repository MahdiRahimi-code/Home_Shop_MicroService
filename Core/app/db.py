# app/db.py  (یا همان جایی که client و db را تعریف کرده‌اید)
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

client = AsyncIOMotorClient(settings.mongo_uri)
db = client.get_default_database()

# در ضمن، اگر نیاز دارید یک شاخص TTL برای حذف خودکارِ تخفیف منقضی‌شده بسازید:
db.discounts.create_index("expiration_date", expireAfterSeconds=0)


# # app/db.py
# from motor.motor_asyncio import AsyncIOMotorClient
# from .config import get_settings

# settings = get_settings()
# client = AsyncIOMotorClient(settings.mongo_uri)

# # حالت صحیح برای انتخاب دیتابیس
# db = client["core_db"]  # ← اینجا نام دیتابیس رو دستی وارد می‌کنی
