"""
Quiz Pydantic schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional


class QuizBase(BaseModel):
    """Base quiz schema"""
    topic_id: str
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    duration_minutes: int = Field(..., ge=1, le=180)


class QuizCreate(QuizBase):
    """Schema for creating a quiz"""
    questions: List[Dict[str, Any]]
    total_points: int = Field(..., ge=0)


class QuizUpdate(BaseModel):
    """Schema for updating a quiz"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=180)
    questions: Optional[List[Dict[str, Any]]] = None
    total_points: Optional[int] = Field(None, ge=0)


class QuizResponse(QuizBase):
    """Schema for quiz response"""
    id: str
    questions: List[Dict[str, Any]]
    total_points: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuizAttemptCreate(BaseModel):
    """Schema for creating a quiz attempt"""
    quiz_id: str
    student_id: str
    started_at: datetime


class QuizAttemptSubmit(BaseModel):
    """Schema for submitting quiz answers"""
    answers: Dict[str, str]  # question_id: answer


class QuizAttemptResponse(BaseModel):
    """Schema for quiz attempt response"""
    id: str
    quiz_id: str
    student_id: str
    answers: Dict[str, Any]
    score: int
    max_score: int
    time_taken_seconds: int
    started_at: datetime
    submitted_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
