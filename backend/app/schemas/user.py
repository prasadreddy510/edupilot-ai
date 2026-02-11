"""
User Pydantic schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

from app.models.user import UserType


class UserBase(BaseModel):
    """Base user schema"""
    phone_number: str = Field(..., min_length=10, max_length=15)
    user_type: UserType


class UserCreate(UserBase):
    """Schema for creating a user"""
    pass


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    is_active: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: str
    is_active: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
