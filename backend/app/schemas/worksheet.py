"""
Worksheet Pydantic schemas
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator


class WorksheetGenerateRequest(BaseModel):
    """Request to generate a new worksheet"""
    topic_id: str = Field(..., description="Topic ID to generate worksheet for")
    num_questions: int = Field(10, ge=5, le=20, description="Number of questions")
    difficulty: str = Field("medium", description="Difficulty level: easy, medium, hard")

    @validator("difficulty")
    def validate_difficulty(cls, v):
        if v not in ["easy", "medium", "hard"]:
            raise ValueError("Difficulty must be easy, medium, or hard")
        return v


class WorksheetResponse(BaseModel):
    """Worksheet response with questions"""
    id: str
    student_id: str
    topic_id: str
    title: str
    difficulty: str
    total_questions: int
    max_score: int
    questions: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WorksheetListResponse(BaseModel):
    """Simplified worksheet list item"""
    id: str
    title: str
    topic_id: str
    topic_name: str
    difficulty: str
    total_questions: int
    max_score: int
    created_at: datetime
    is_submitted: bool
    latest_score: Optional[float] = None
    latest_percentage: Optional[float] = None


class WorksheetSubmitRequest(BaseModel):
    """Request to submit worksheet answers"""
    answers: Dict[str, str] = Field(
        ..., description="Map of question_number to student answer"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "answers": {
                    "1": "Chlorophyll",
                    "2": "The sunlight provides energy for the photosynthesis process",
                    "3": "True",
                }
            }
        }


class WorksheetSubmissionResponse(BaseModel):
    """Worksheet submission with grading results"""
    id: str
    worksheet_id: str
    student_id: str
    answers: Dict[str, str]
    score: float
    max_score: int
    percentage: float
    graded_answers: List[Dict[str, Any]]
    passed: bool
    submitted_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
