"""
Progress and WeakArea Pydantic schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ProgressRecordBase(BaseModel):
    """Base progress record schema"""
    student_id: str
    topic_id: str
    mastery_level: float = Field(..., ge=0.0, le=100.0)
    total_time_spent_seconds: int = Field(default=0, ge=0)
    quiz_count: int = Field(default=0, ge=0)
    worksheet_count: int = Field(default=0, ge=0)
    average_quiz_score: float = Field(default=0.0, ge=0.0, le=100.0)
    average_worksheet_score: float = Field(default=0.0, ge=0.0, le=100.0)
    last_practiced_at: Optional[datetime] = None


class ProgressRecordCreate(ProgressRecordBase):
    """Schema for creating a progress record"""
    pass


class ProgressRecordUpdate(BaseModel):
    """Schema for updating a progress record"""
    mastery_level: Optional[float] = Field(None, ge=0.0, le=100.0)
    total_time_spent_seconds: Optional[int] = Field(None, ge=0)
    quiz_count: Optional[int] = Field(None, ge=0)
    worksheet_count: Optional[int] = Field(None, ge=0)
    average_quiz_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    average_worksheet_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    last_practiced_at: Optional[datetime] = None


class ProgressRecordResponse(ProgressRecordBase):
    """Schema for progress record response"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WeakAreaBase(BaseModel):
    """Base weak area schema"""
    student_id: str
    topic_id: str
    mastery_level: float = Field(..., ge=0.0, le=100.0)


class WeakAreaCreate(WeakAreaBase):
    """Schema for creating a weak area"""
    pass


class WeakAreaResponse(WeakAreaBase):
    """Schema for weak area response"""
    id: str
    identified_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
