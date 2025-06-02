import os
import grpc
from app.iam import iam_pb2, iam_pb2_grpc
from fastapi import Header, HTTPException, status
from jose import jwt, JWTError

# env config
IAM_HOST = os.getenv("IAM_GRPC_HOST", "localhost")
IAM_PORT = os.getenv("IAM_GRPC_PORT", "50051")
SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

# gRPC channel
channel = grpc.aio.insecure_channel(f"{IAM_HOST}:{IAM_PORT}")
stub = iam_pb2_grpc.IAMServiceStub(channel)  # ← برای استفاده در APIها

# تابع گرفتن کاربر از روی توکن JWT
# async def get_current_user(authorization: str = Header(...)):
#     if not authorization.startswith("Bearer "):
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#     token = authorization.split(" ", 1)[1]

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = int(payload["sub"])
#     except JWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

#     try:
#         response = await stub.GetUser(iam_pb2.GetUserRequest(user_id=user_id))
#     except grpc.RpcError as e:
#         raise HTTPException(status_code=502, detail=f"IAM gRPC error: {e.code().name}")

#     return {
#         "id": response.id,
#         "name": response.name,
#         "email": response.email,
#         "city": response.city,
#         "is_active": response.is_active,
#         "avatar_url": response.avatar_url
#     }
