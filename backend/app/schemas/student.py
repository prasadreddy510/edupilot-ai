"""
Student Pydantic schemas
"""

from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional


class StudentBase(BaseModel):
    """Base student schema"""
    name: str = Field(..., min_length=1, max_length=100)
    grade: int = Field(..., ge=3, le=10)
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None


class StudentCreate(StudentBase):
    """Schema for creating a student"""
    user_id: str


class StudentUpdate(BaseModel):
    """Schema for updating a student"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    grade: Optional[int] = Field(None, ge=3, le=10)
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None


class StudentResponse(StudentBase):
    """Schema for student response"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
