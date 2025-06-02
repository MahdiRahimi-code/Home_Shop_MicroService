import grpc
from iam_pb2_grpc import IAMServiceServicer
from iam_pb2 import GetUserResponse
from models.user import User
from models.admin import Admin
from Database import SessionLocal
from iam_pb2 import (
    AdminCheckResponse,
    DeleteUserResponse,
    BanUserResponse
)

class IAMService(IAMServiceServicer):
    def GetUser(self, request, context):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == request.user_id).first()
            if not user:
                context.abort(grpc.StatusCode.NOT_FOUND, "User not found")
            return GetUserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                city=user.city,
                is_active=user.is_active,
                avatar_url=user.avatar_url or ""
            )
        finally:
            db.close()
    
    async def CheckAdmin(self, request, context):
        db = SessionLocal()
        try:
            admin = db.query(Admin).filter(Admin.id == request.admin_id).first()
            if not admin:
                context.abort(grpc.StatusCode.NOT_FOUND, "Admin not found")
            return AdminCheckResponse(id=admin.id, email=admin.email, is_admin=True)
        finally:
            db.close()

    async def DeleteUser(self, request, context):
        db = SessionLocal()
        user = db.query(User).filter(User.id == request.user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return DeleteUserResponse(success=True)
        return DeleteUserResponse(success=False)

    async def BanUser(self, request, context):
        db = SessionLocal()
        user = db.query(User).filter(User.id == request.user_id).first()
        if user:
            user.is_active = False
            db.commit()
            return BanUserResponse(success=True)
        return BanUserResponse(success=False)

