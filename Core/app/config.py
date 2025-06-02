from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import AnyUrl


class Settings(BaseSettings):
    iam_base_url: AnyUrl = "http://localhost:8000"
    mongo_uri: str = "mongodb://root:admin@localhost:27017/core_db?authSource=admin"
    iam_jwks_url: AnyUrl = "http://localhost:8000/.well-known/jwks.json"

    model_config = {
        "env_file": ".env",
        "extra": "allow",  # ← اجازه می‌ده فیلدهای اضافه در فایل env باشن
    }


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
print("Mongo URI:", settings.mongo_uri)  # ← برای دیباگ
