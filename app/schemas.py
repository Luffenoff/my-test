from pydantic import BaseModel, Field


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
    use_digits: bool = Field(default = True)
    use_special: bool = Field(default = False)