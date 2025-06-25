# core/settings.py

import os

# IAM Service (مدیریت کاربران)
IAM_GRPC_HOST = os.getenv("IAM_GRPC_HOST", "localhost")
IAM_GRPC_PORT = int(os.getenv("IAM_GRPC_PORT", 50051))

# Media Service (مدیریت فایل‌های مدیا)
# MEDIA_GRPC_HOST = os.getenv("MEDIA_GRPC_HOST", "localhost")
# MEDIA_GRPC_PORT = int(os.getenv("MEDIA_GRPC_PORT", 50052))


from pydantic_settings import BaseSettings  # تغییر این خط
# اگر از فایل env استفاده می‌کنی:
from pydantic_settings import SettingsConfigDict


class Settings(BaseSettings):
    MEDIA_GRPC_HOST: str = "localhost"
    MEDIA_GRPC_PORT: int = 50052
    # IAM_GRPC_HOST: str = "localhost"
    # IAM_GRPC_PORT: int = 50051

    # model_config = SettingsConfigDict(env_file=".env")  # اگر از .env استفاده می‌کنی


settings = Settings()

