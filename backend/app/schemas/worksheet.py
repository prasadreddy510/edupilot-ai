"""
Worksheet Pydantic schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional

from app.models.worksheet import DifficultyLevel


class QuestionSchema(BaseModel):
    """Schema for a question"""
    id: str
    question_text: str
    question_type: str  # mcq, short_answer, numerical, true_false
    options: Optional[List[str]] = None
    correct_answer: str
    points: int = Field(..., ge=0)


class WorksheetBase(BaseModel):
    """Base worksheet schema"""
    student_id: str
    topic_id: str
    title: str = Field(..., min_length=1, max_length=200)
    difficulty_level: DifficultyLevel = DifficultyLevel.MEDIUM


class WorksheetCreate(WorksheetBase):
    """Schema for creating a worksheet"""
    questions: List[QuestionSchema]
    total_points: int = Field(..., ge=0)


class WorksheetResponse(WorksheetBase):
    """Schema for worksheet response"""
    id: str
    questions: List[Dict[str, Any]]
    total_points: int
    created_at: datetime

    class Config:
        from_attributes = True


class WorksheetSubmissionCreate(BaseModel):
    """Schema for submitting worksheet answers"""
    worksheet_id: str
    student_id: str
    answers: Dict[str, str]  # question_id: answer


class WorksheetSubmissionResponse(BaseModel):
    """Schema for worksheet submission response"""
    id: str
    worksheet_id: str
    student_id: str
    answers: Dict[str, Any]
    score: int
    max_score: int
    feedback: Optional[Dict[str, Any]] = None
    submitted_at: datetime
    graded_at: Optional[datetime] = None

    class Config:
        from_attributes = True
