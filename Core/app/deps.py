from .db import db
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.iam_client import stub  # gRPC stub
from app.iam import iam_pb2  # gRPC message definitions
from jose import jwt, JWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/user/iam/login")

async def get_db():
    return db

# def decode_access_token(token: str):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload.get("sub")
#     except JWTError:
#         return None


SECRET_KEY = "super-secret-key"  # همینو IAM استفاده کرده؟
ALGORITHM = "HS256"

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload["sub"]
    except JWTError as e:
        print("JWT Decode Error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:

    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    try:
        user_id = decode_token(token)
        req = iam_pb2.GetUserRequest(user_id=int(user_id))
        res = await stub.GetUser(req)
    except HTTPException:
        raise  # برای JWTError
    except Exception as e:
        print("gRPC error:", e)
        raise HTTPException(status_code=502, detail="gRPC IAM service unavailable")

    return {
        "id": res.id,
        "name": res.name,
        "email": res.email,
        "city": res.city,
        "is_active": res.is_active
    }


CurrentUser = get_current_user


from app.iam import iam_pb2

oauth2_scheme_admin = OAuth2PasswordBearer(
    tokenUrl="http://localhost:8000/admin/iam/login"      # مسیر لاگین ادمین در IAM
)

async def get_current_admin(token: str = Depends(oauth2_scheme_admin)) -> dict:
    # print(token)

    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info(f"Admin token: {token}")

    if not token:
        raise HTTPException(status_code=401, detail="Missing admin token")

    admin_id = decode_token(token)

    try:
        req = iam_pb2.AdminCheckRequest(admin_id=int(admin_id))
        res = await stub.CheckAdmin(req)          # باید در IAM پیاده شده باشد
    except Exception:
        raise HTTPException(status_code=502, detail="IAM gRPC unavailable")

    if not res.is_admin:
        raise HTTPException(status_code=403, detail="Not an admin")

    return {"id": res.id, "email": res.email}

CurrentAdmin = get_current_admin


# # app/deps.py

# from .db import db
# from .iam_client import get_current_user

# async def get_db():
#     return db

# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from app.config import settings
# import httpx

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://localhost:8000/user/iam/login")

# async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(
#                 f"{settings.iam_base_url}/user/iam/me",
#                 headers={"Authorization": f"Bearer {token}"},
#             )
#     except httpx.RequestError:
#         raise HTTPException(status_code=500, detail="IAM service unavailable")

#     if response.status_code != 200:
#         raise HTTPException(status_code=401, detail="Invalid token")

#     return response.json()

# CurrentUser = get_current_user
