from pydantic import BaseModel


class UserBase(BaseModel):
    username: str
    
    
class UserCreate(BaseModel):
    password: str
    
    
class UserResponse(UserBase):
    id: int
    
    
    class Config:
        from_attributes = True
        
        
class PasswordCreate(BaseModel):
    length: int
    use_digits: True
    use_special: False