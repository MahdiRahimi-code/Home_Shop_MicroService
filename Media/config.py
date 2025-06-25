# config.py
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    mongo_uri: str = Field("mongodb://root:admin@localhost:27017/media_db?authSource=admin", env="MONGO_URL")
    grpc_port: int = Field(50052, env="GRPC_PORT")

    model_config = {
        "env_file": ".env",
        "extra": "allow",
    }


@lru_cache
def get_settings():
    return Settings()
