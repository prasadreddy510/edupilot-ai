"""
Subject Pydantic schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class SubjectBase(BaseModel):
    """Base subject schema"""
    name: str = Field(..., min_length=1, max_length=100)
    grade: int = Field(..., ge=3, le=10)
    description: Optional[str] = None
    icon: Optional[str] = None


class SubjectCreate(SubjectBase):
    """Schema for creating a subject"""
    pass


class SubjectUpdate(BaseModel):
    """Schema for updating a subject"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    grade: Optional[int] = Field(None, ge=3, le=10)
    description: Optional[str] = None
    icon: Optional[str] = None


class SubjectResponse(SubjectBase):
    """Schema for subject response"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
