"""
Progress and WeakArea Pydantic schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any


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


class WeakAreaResponse(BaseModel):
    """Schema for weak area response from analytics"""
    topic_id: str
    topic_name: str
    subject: Optional[str] = None
    mastery_score: float = Field(..., ge=0.0, le=100.0)
    reasons: List[str] = Field(default_factory=list, description="Specific weaknesses identified")
    priority: int = Field(..., ge=0, le=200, description="Priority score (higher = more urgent)")


class MasteryComponents(BaseModel):
    """Breakdown of mastery score components"""
    quiz_score: float = Field(default=0.0, ge=0.0, le=100.0)
    worksheet_score: float = Field(default=0.0, ge=0.0, le=100.0)
    consistency: float = Field(default=0.0, ge=0.0, le=100.0)
    retention: float = Field(default=0.0, ge=0.0, le=100.0)


class MasteryAttempts(BaseModel):
    """Count of attempts used in mastery calculation"""
    quizzes: int = 0
    worksheets: int = 0
    sessions: int = 0


class MasteryCalculationResponse(BaseModel):
    """Schema for mastery level calculation response"""
    topic_id: str
    mastery_score: float = Field(..., ge=0.0, le=100.0)
    mastery_level: str = Field(..., description="beginner, learning, proficient, or mastered")
    components: MasteryComponents
    attempts: MasteryAttempts
    error: Optional[str] = None


class StudentAnalyticsResponse(BaseModel):
    """Schema for comprehensive student analytics"""
    total_learning_time_minutes: int = 0
    topics_studied: int = 0
    topics_completed: int = 0
    average_quiz_score: float = Field(default=0.0, ge=0.0, le=100.0)
    average_worksheet_score: float = Field(default=0.0, ge=0.0, le=100.0)
    weekly_time_minutes: int = 0
    weekly_sessions: int = 0
    overall_progress: float = Field(default=0.0, ge=0.0, le=100.0)


class SubjectBreakdownResponse(BaseModel):
    """Schema for subject-wise progress breakdown"""
    subject: str
    topics_studied: int = 0
    topics_mastered: int = 0
    average_mastery: float = Field(default=0.0, ge=0.0, le=100.0)
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)


class ProgressUpdateRequest(BaseModel):
    """Schema for requesting a progress update"""
    pass
