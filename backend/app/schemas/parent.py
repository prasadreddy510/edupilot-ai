"""
Parent Pydantic schemas
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class ParentBase(BaseModel):
    """Base parent schema"""
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class ParentCreate(ParentBase):
    """Schema for creating a parent"""
    user_id: str


class ParentUpdate(BaseModel):
    """Schema for updating a parent"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None


class ParentResponse(ParentBase):
    """Schema for parent response"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
