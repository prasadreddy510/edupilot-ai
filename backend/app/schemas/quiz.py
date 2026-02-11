"""
Quiz Pydantic schemas
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator


class QuizGenerateRequest(BaseModel):
    """Request to generate a new quiz"""
    topic_id: str = Field(..., description="Topic ID to generate quiz for")
    num_questions: int = Field(10, description="Number of questions (5, 10, 15, 20)")
    difficulty: str = Field("medium", description="Difficulty level: easy, medium, hard")

    @validator("num_questions")
    def validate_num_questions(cls, v):
        if v not in [5, 10, 15, 20]:
            raise ValueError("Number of questions must be 5, 10, 15, or 20")
        return v

    @validator("difficulty")
    def validate_difficulty(cls, v):
        if v not in ["easy", "medium", "hard"]:
            raise ValueError("Difficulty must be easy, medium, or hard")
        return v


class QuizResponse(BaseModel):
    """Quiz response with questions"""
    id: str
    student_id: str
    topic_id: str
    title: str
    difficulty: str
    total_questions: int
    duration_minutes: int
    max_score: int
    questions: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuizListResponse(BaseModel):
    """Simplified quiz list item"""
    id: str
    title: str
    topic_id: str
    topic_name: str
    difficulty: str
    total_questions: int
    duration_minutes: int
    max_score: int
    created_at: datetime
    total_attempts: int
    best_score: Optional[float] = None
    latest_score: Optional[float] = None


class QuizAttemptStart(BaseModel):
    """Response when starting a quiz attempt"""
    attempt_id: str
    started_at: datetime


class QuizSubmitRequest(BaseModel):
    """Request to submit quiz answers"""
    attempt_id: str = Field(..., description="Quiz attempt ID")
    answers: Dict[str, str] = Field(
        ..., description="Map of question_number to student answer"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "880e8400-e29b-41d4-a716-446655440000",
                "answers": {
                    "1": "Option A",
                    "2": "True",
                    "3": "Option C",
                }
            }
        }


class QuizAttemptResponse(BaseModel):
    """Quiz attempt with grading results"""
    id: str
    quiz_id: str
    student_id: str
    started_at: datetime
    submitted_at: Optional[datetime] = None
    answers: Dict[str, str]
    score: Optional[int] = None
    max_score: Optional[int] = None
    percentage: Optional[float] = None
    graded_answers: Optional[List[Dict[str, Any]]] = None
    passed: Optional[bool] = None
    time_taken_seconds: Optional[int] = None
    time_exceeded: Optional[bool] = None
    improvement_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuizStatsResponse(BaseModel):
    """Quiz statistics across all attempts"""
    quiz_id: str
    total_attempts: int
    best_score: float
    average_score: float
    latest_score: float
    improvement_trend: float  # Positive = improving, Negative = declining
    average_time_seconds: float
