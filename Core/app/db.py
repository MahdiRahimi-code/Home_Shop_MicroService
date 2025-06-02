# app/db.py
from motor.motor_asyncio import AsyncIOMotorClient
from .config import get_settings

settings = get_settings()
client = AsyncIOMotorClient(settings.mongo_uri)

# حالت صحیح برای انتخاب دیتابیس
db = client["core_db"]  # ← اینجا نام دیتابیس رو دستی وارد می‌کنی
