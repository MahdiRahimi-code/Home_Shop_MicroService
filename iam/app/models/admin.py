from sqlalchemy import Column, Integer, String
from Database import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
