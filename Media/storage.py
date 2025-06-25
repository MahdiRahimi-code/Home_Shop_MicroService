### storage.py
import os

BASE_URL = os.getenv("MEDIA_BASE_URL", "http://localhost:8002/media")
MEDIA_ROOT = os.getenv("MEDIA_ROOT", "./media_storage")


def save_file(rel_path: str, data: bytes):
    path = os.path.join(MEDIA_ROOT, rel_path)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def remove_file(rel_path: str):
    path = os.path.join(MEDIA_ROOT, rel_path)
    if os.path.exists(path):
        os.remove(path)
