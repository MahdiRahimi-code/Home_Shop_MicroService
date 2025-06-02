from sqlalchemy import Column, Integer, String, Boolean
from Database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone_number = Column(String)
    city = Column(String)
    is_active = Column(Boolean, default=True)
    avatar_url = Column(String)
    # token = Column(String, unique=True)  # JWT Token stored in the database
