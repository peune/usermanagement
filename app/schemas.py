from typing import Optional, Any
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime

class UserBase(BaseModel):
    name: str = Field(..., max_length=100)
    family_name: str = Field(..., max_length=100)
    email: EmailStr 
    workplace: str = Field(..., max_length=255)
    position: str = Field(..., max_length=100)
    note: Optional[str] = None

    class Config:
        from_attributes=True
        orm_mode=True

    @validator("email")
    def email_length(cls, v):
        if len(v) > 255:
            raise ValueError("Email must be at most 255 characters")
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=4)
    class Config:
        from_attributes=True
        orm_mode=True

class User(UserBase):
    id: int
    is_approved: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes=True
        orm_mode=True

    @validator('created_at', pre=True)
    def parse_created_at(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            # Handle string format from database
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value

class UserApprovalResponse(BaseModel):
    user: User 
    new_token: str 

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None