# app/routers/profile.py
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from app.deps import CurrentUser
from app.iam_client import stub
from app.deps import get_iam_stub
from app.iam.iam_pb2_grpc import IAMServiceStub
from app.iam import iam_pb2
from app.rabit import publish_event
import uuid, os

import grpc
from app.deps import get_iam_stub
from app.iam.iam_pb2 import UpdateUserRequest
from google.protobuf import empty_pb2
from app.media import media_pb2, media_pb2_grpc
from app.iam import iam_pb2, iam_pb2_grpc
from app.deps import CurrentUser, get_iam_stub, get_media_stub
from settings import settings


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/", response_model=dict)
async def visit_profile(user=Depends(CurrentUser)):
    # کاربر (user) را به‌صورت دیکشنری (json) دریافت می‌کنیم
    return user


@router.patch("/", response_model=dict)
async def edit_profile(payload: dict, user=Depends(CurrentUser)):
    req = iam_pb2.UpdateUserRequest(user_id=user["id"], fields=payload)
    try:
        await stub.UpdateUser(req)
    except Exception:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="IAM update failed")
    await publish_event("user.updated", {"user_id": user["id"], **payload})
    return {"detail": "updated"}



@router.post("/test-media-meta", response_model=dict)
async def test_media_meta(
    media_stub: media_pb2_grpc.MediaServiceStub = Depends(get_media_stub)
):
    try:
        response = await media_stub.SaveProfilePictureMeta(
            media_pb2.ProfilePictureMetaRequest(user_id=123, filename="example.jpg")
        )
        return {
            "status": "success",
            "url": response.url,
            "media_id": response.media_id
        }
    except grpc.RpcError as e:
        return {
            "status": "failed",
            "grpc_code": e.code().name,
            "grpc_details": e.details()
        }



@router.post("/picture", response_model=dict)
async def set_profile_picture(
    filename: str,
    user=Depends(CurrentUser),
    media_stub: media_pb2_grpc.MediaServiceStub = Depends(get_media_stub),
    iam_stub: IAMServiceStub = Depends(get_iam_stub),
):
    # 1️⃣ ذخیره متادیتا در سرویس media
    try:
        media_resp = await media_stub.SaveProfilePictureMeta(
            media_pb2.ProfilePictureMetaRequest(
                user_id=user["id"],
                filename=filename,
            )
        )
    except grpc.RpcError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Media metadata save failed: {e.code().name}"
        )

    # 2️⃣ به‌روزرسانی avatar_url در سرویس IAM
    # try:
    #     await iam_stub.UpdateUser(
    #         UpdateUserRequest(
    #             user_id=user["id"],
    #             fields={"avatar_url": media_resp.url},
    #         )
    #     )
    # except grpc.RpcError as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_502_BAD_GATEWAY,
    #         detail=f"IAM update failed: {e.code().name}"
        # )

    # 3️⃣ انتشار رویداد در RabbitMQ
    await publish_event("user.avatar_uploaded", {
        "user_id": user["id"],
        "avatar_url": media_resp.url
    })

    return {"avatar_url": media_resp.url}


# @router.post("/picture", response_model=dict)
# async def set_profile_picture(
#     filename: str,
#     user=Depends(CurrentUser),
#     media_stub: media_pb2_grpc.MediaServiceStub = Depends(get_media_stub)):

#     try:
#         response = await media_stub.SaveProfilePictureMeta(
#             media_pb2.ProfilePictureMetaRequest(
#                 user_id=user["id"],
#                 filename=filename,
#             )
#         )
#     except grpc.RpcError as e:
#         raise HTTPException(
#             status_code=status.HTTP_502_BAD_GATEWAY,
#             detail=f"Media metadata save failed: {e.code().name}"
#         )

#     # حالا فقط URL رو در IAM ذخیره کن
#     try:
#         await stub.UpdateUser(
#             UpdateUserRequest(
#                 user_id=user["id"],
#                 fields={"avatar_url": response.url},
#             )
#         )
#     except grpc.RpcError:
#         raise HTTPException(
#             status_code=status.HTTP_502_BAD_GATEWAY,
#             detail="IAM update failed"
#         )

#     await publish_event("user.avatar_uploaded", {
#         "user_id": user["id"],
#         "avatar_url": response.url
#     })
#     return {"avatar_url": response.url}



# @router.post("/picture", response_model=dict)
# async def add_profile_picture(
#     file: UploadFile = File(...),
#     user=Depends(CurrentUser),
#     media_stub: media_pb2_grpc.MediaServiceStub = Depends(get_media_stub),
# ):
#     try:
#         content: bytes = await file.read()
#         ext = os.path.splitext(file.filename)[1] or ".jpg"
#         filename = f"{uuid.uuid4()}{ext}"

#         # فراخوانی gRPC برای آپلود عکس
#         grpc_response = await media_stub.UploadProfilePicture(
#             media_pb2.UploadProfilePictureRequest(
#                 user_id=user["id"],
#                 filename=filename,
#                 data=content,
#             )
#         )
#         avatar_url = grpc_response.url

        
#         await iam_pb2.UpdateUser(
#             UpdateUserRequest(
#                 user_id=user["id"],
#                 fields={"avatar_url": avatar_url},
#             )
#         )

#         # انتشار رویداد در RabbitMQ
#         await publish_event("user.avatar_uploaded", {
#             "user_id": user["id"],
#             "avatar_url": avatar_url
#         })

#         return {"avatar_url": avatar_url}

#     except grpc.RpcError as e:
#         raise HTTPException(
#             status_code=status.HTTP_502_BAD_GATEWAY,
#             detail=f"Media service error: {e.code().name}"
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=str(e)
#         )


# @router.post("/picture", response_model=dict)
# async def add_profile_picture(file: UploadFile = File(...), user=Depends(CurrentUser)):
#     ext = os.path.splitext(file.filename)[1]
#     filename = f"{uuid.uuid4()}{ext}"
#     content = await file.read()
#     path = f"/tmp/{filename}"
#     # with open(path, "wb") as f:
#     #     f.write(content)

#     # avatar_url = f"https://cdn.example.com/{filename}"

#     # write to /tmp, then call IAM

#     with open(path, "wb") as f: 
#         f.write(content)
#     avatar_url = f"https://cdn.example.com/{filename}"
#     import grpc, proto.media_pb2, proto.media_pb2_grpc

#     channel = grpc.aio.insecure_channel(f"{settings.MEDIA_GRPC_HOST}:{settings.MEDIA_GRPC_PORT}")
#     media_stub = proto.media_pb2_grpc.MediaServiceStub(channel)
#     response = await media_stub.UploadProfilePicture(
#         proto.media_pb2.UploadProfilePictureRequest(
#             user_id=user["id"], filename=file.filename, data=content
#         )
#     )
#     avatar_url = response.url


#     req = iam_pb2.UpdateUserRequest(
#         user_id=user["id"],
#         fields={"avatar_url": avatar_url}
#     )
#     try:
#         await stub.UpdateUser(req)
#     except Exception:
#         raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="IAM update failed")
#     await publish_event("user.avatar_uploaded", {"user_id": user["id"], "avatar_url": avatar_url})
#     return {"avatar_url": avatar_url}


@router.get("/profile", response_model=dict)
async def get_profile(user=Depends(CurrentUser)):
    return user





# from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
# from app.deps import CurrentUser
# # from app.iam_client import _stub, iam_pb2
# from app.iam_client import stub
# from app.iam import iam_pb2
# from app.rabit import publish_event
# import uuid, os

# router = APIRouter(prefix="/profile", tags=["profile"])

# @router.get("/", response_model=dict)
# async def visit_profile(user=Depends(CurrentUser)):
#     return user

# @router.patch("/", response_model=dict)
# async def edit_profile(payload: dict, user=Depends(CurrentUser)):
#     req = iam_pb2.UpdateUserRequest(user_id=user["id"], fields=payload)
#     try:
#         await stub.UpdateUser(req)
#     except Exception:
#         raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="IAM update failed")
#     await publish_event("user.updated", {"user_id": user["id"], **payload})
#     return {"detail": "updated"}

# @router.post("/picture", response_model=dict)
# async def add_profile_picture(file: UploadFile = File(...), user=Depends(CurrentUser)):
#     ext = os.path.splitext(file.filename)[1]
#     filename = f"{uuid.uuid4()}{ext}"
#     content = await file.read()
#     path = f"/tmp/{filename}"
#     with open(path, "wb") as f:
#         f.write(content)

#     avatar_url = f"https://cdn.example.com/{filename}"
#     req = iam_pb2.UpdateUserRequest(
#         user_id=user["id"],
#         fields={"avatar_url": avatar_url}
#     )
#     try:
#         await stub.UpdateUser(req)
#     except Exception:
#         raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="IAM update failed")
#     await publish_event("user.avatar_uploaded", {"user_id": user["id"], "avatar_url": avatar_url})
#     return {"avatar_url": avatar_url}

# from app.deps import CurrentUser

# @router.get("/profile")
# async def get_profile(user=Depends(CurrentUser)):
#     return user


