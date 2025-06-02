from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from app.deps import CurrentUser
# from app.iam_client import _stub, iam_pb2
from app.iam_client import stub
from app.iam import iam_pb2
from app.rabit import publish_event
import uuid, os

router = APIRouter(prefix="/profile", tags=["profile"])

@router.get("/", response_model=dict)
async def visit_profile(user=Depends(CurrentUser)):
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

@router.post("/picture", response_model=dict)
async def add_profile_picture(file: UploadFile = File(...), user=Depends(CurrentUser)):
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    content = await file.read()
    path = f"/tmp/{filename}"
    with open(path, "wb") as f:
        f.write(content)

    avatar_url = f"https://cdn.example.com/{filename}"
    req = iam_pb2.UpdateUserRequest(
        user_id=user["id"],
        fields={"avatar_url": avatar_url}
    )
    try:
        await stub.UpdateUser(req)
    except Exception:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="IAM update failed")
    await publish_event("user.avatar_uploaded", {"user_id": user["id"], "avatar_url": avatar_url})
    return {"avatar_url": avatar_url}

from app.deps import CurrentUser

@router.get("/profile")
async def get_profile(user=Depends(CurrentUser)):
    return user


