from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from Database import SessionLocal
from crud import user as user_crud
from auth.jwt_handler import create_access_token, create_refresh_token, decode_access_token
from auth.password_utils import verify_password, hash_password
from models.user import User
from schemas.user import UserCreate, UserOut, UserOutToken, UserSignupRequest, OTPVerify, otpStatus, SignupVerifiedOtp
from utils.otp import generate_otp, send_otp_email, store_otp, verify_otp

router = APIRouter(prefix="/user", tags=["User"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/iam/login")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@router.post("/iam/verifyOTP", response_model=otpStatus)
def verify_sent_otp(data:OTPVerify, db: Session = Depends(get_db)):
    if not verify_otp(data.email, data.otp):
        raise HTTPException(status_code=400, detail="Invalid OTP")
    return {"status": "ok"}


@router.post("/iam/signup", response_model=UserOutToken)
def signup_with_otp(data: SignupVerifiedOtp, db: Session = Depends(get_db)):
    # if not verify_otp(data.email, data.otp):
    #     raise HTTPException(status_code=400, detail="Invalid OTP")
    if data.status != "ok":
        raise HTTPException(status_code=400, detail="Invalid OTP")

    user_data = UserCreate(**data.dict(exclude={"otp"}))
    db_user, access_token, refresh_token = user_crud.create_user(db, user_data)

    return {
        "id": db_user.id,
        "name": db_user.name,
        "email": db_user.email,
        "city": db_user.city,
        "is_active": db_user.is_active,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@router.post("/iam/login", response_model=UserOutToken)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, form_data.username)

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "city": user.city,
        "is_active": user.is_active,
        "access_token": access_token,
        "refresh_token": refresh_token
        # "token_type": "bearer"
    }


@router.post("/iam/reset-password")
def reset_password(email: str, new_password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.password = hash_password(new_password)
    db.commit()
    return {"message": "Password reset successful"}

# # User login route
# @router.post("/login", response_model=UserOut)
# def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
#     user = user_crud.get_user_by_email(db, form_data.username)
#     if not user or not verify_password(form_data.password, user.password):
#         raise HTTPException(status_code=401, detail="Invalid email or password")
    
#     # Generate access and refresh tokens for the logged-in user
#     access_token = create_access_token({"sub": str(user.id)})
#     refresh_token = create_refresh_token({"sub": str(user.id)})
    
#     return {
#         "access_token": access_token,
#         "refresh_token": refresh_token,
#         "token_type": "bearer"
#     }

@router.post("/iam/refresh_token")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    try:
        SECRET_KEY = "super-secret-key"
        ALGORITHM = "HS256"
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        new_access_token = create_access_token({"sub": str(user.id)})
        return {"access_token": new_access_token, "token_type": "bearer"}
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


@router.get("/iam/me", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/iam/signup-request")
def signup_request(user: UserSignupRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    existing_user = user_crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    from utils.otp import r
    if r.exists(f"otp:{user.email}"):
        raise HTTPException(
            status_code=429,
            detail="An OTP has already been sent. Please wait until it expires."
        )

    otp = generate_otp()
    store_otp(user.email, otp)
    background_tasks.add_task(send_otp_email, user.email, otp)

    return {"message": "OTP sent to your email"}
