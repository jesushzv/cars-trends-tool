"""
Authentication schemas
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    token_type: str
    expires_in: int


class TokenData(BaseModel):
    """Token data schema"""
    username: Optional[str] = None


class UserBase(BaseModel):
    """Base user schema"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """User creation schema"""
    password: str


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema"""
    id: str
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserInDB(UserResponse):
    """User in database schema"""
    hashed_password: str
