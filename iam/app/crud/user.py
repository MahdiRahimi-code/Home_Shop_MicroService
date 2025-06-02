from sqlalchemy.orm import Session
from models.user import User
from schemas.user import UserCreate
from auth.jwt_handler import create_access_token, create_refresh_token
from auth.password_utils import hash_password


def create_user(db: Session, user: UserCreate):
    hashed_password = hash_password(user.password)
    
    data = user.dict(exclude={"password"})
    
    db_user = User(**data, password=hashed_password)
    
    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user, access_token, refresh_token


# def create_user(db: Session, user: UserCreate):
#     # Hash the password before saving
#     hashed_password = hash_password(user.password)
    
#     # Exclude the password field from user.dict() to avoid duplication
#     data = user.dict(exclude={"password"})
    
#     # Create the user instance with hashed password
#     db_user = User(**data, password=hashed_password)
    
#     # Generate access and refresh tokens
#     access_token = create_access_token({"sub": str(db_user.id)})
#     refresh_token = create_refresh_token({"sub": str(db_user.id)})
    
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)

#     return db_user, access_token, refresh_token

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# def user_login_auth(db:Session, email:str, password:str):
#     user = db.query(User).filter(User.email == email).first()
#     if user and user.password==password:
#         return user
#     return None