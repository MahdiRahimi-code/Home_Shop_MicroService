from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from Database import SessionLocal
from models.admin import Admin
from auth.password_utils import verify_password
from auth.jwt_handler import create_access_token, create_refresh_token
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

router = APIRouter(prefix="/admin", tags=["Admin"])
oauth2_scheme_admin = OAuth2PasswordBearer(tokenUrl="admin/iam/login")

SECRET_KEY = "super-secret-key"
ALGORITHM = "HS256"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# @router.post("/login")
# def admin_login(credentials: AdminLogin, db: Session = Depends(get_db)):
#     admin = db.query(Admin).filter(Admin.email == credentials.email).first()
#     if not admin or admin.password != credentials.password:
#         raise HTTPException(status_code=401, detail="Invalid email or password")
    
#     access_token = create_access_token({"sub": str(admin.email)})
#     refresh_token = create_refresh_token({"sub": str(admin.email)})

#     return {"message": f"Welcome Dear Admin!"}

#     user = user_crud.get_user_by_email(db, form_data.username)

#     if not user or not verify_password(form_data.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid email or password")
    
    
@router.post("/iam/login")
def admin_login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.email == form_data.username).first()

    if not admin or not verify_password(form_data.password, admin.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token(data={"sub": str(admin.id), "role": "admin"})
    refresh_token = create_refresh_token(data={"sub": str(admin.id), "role": "admin"})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
        # "token_type": "bearer"
    }

@router.post("/refresh_token")
def refresh_access_token(refresh_token: str):
    try:
        SECRET_KEY = "super-secret-key"
        ALGORITHM = "HS256"

        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id = payload.get("sub")
        # role = payload.get("role")

        if not admin_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access_token = create_access_token(data={"sub": str(admin_id), "role": "admin"})
        return {"access_token": new_access_token, 
                "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")    


def get_current_admin(token: str = Depends(oauth2_scheme_admin), db: Session = Depends(get_db)) -> Admin:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        admin_id: str = payload.get("sub")

        if admin_id is None:
            raise HTTPException(status_code=403, detail="Not authorized as admin")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    admin = db.query(Admin).filter(Admin.id == int(admin_id)).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")

    return admin


@router.get("/iam/me")
def get_admin_profile(current_admin: Admin = Depends(get_current_admin)):
    return {
        "id": current_admin.id,
        "email": current_admin.email,
        "password": current_admin.password
    }
