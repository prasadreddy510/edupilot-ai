"""
Topic Pydantic schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TopicBase(BaseModel):
    """Base topic schema"""
    subject_id: str
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    order: int = Field(default=0, ge=0)


class TopicCreate(TopicBase):
    """Schema for creating a topic"""
    pass


class TopicUpdate(BaseModel):
    """Schema for updating a topic"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)


class TopicResponse(TopicBase):
    """Schema for topic response"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
