from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key = True, index = True)
    username = Column(String, unique=True, index = True)
    hashed_password = Column(String)
    passwords = relationship("Password", back_populates="owner")
    
    
class Password(Base):
    __tablename__ = "passwords"
    
    id = Column(Integer, primary_key= True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    Password = Column(String)
    
    
    owner = relationship("User", back_populates="passwords")