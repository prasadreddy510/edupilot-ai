from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LearningSessionCreate(BaseModel):
    topic_id: str = Field(..., description="Topic ID to start learning")


class LearningSessionUpdate(BaseModel):
    completed: Optional[bool] = Field(None, description="Mark session as completed")


class LearningSessionResponse(BaseModel):
    id: str
    student_id: str
    topic_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    completed: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LearningSessionStats(BaseModel):
    total_sessions: int = Field(..., description="Total number of learning sessions")
    total_time_minutes: int = Field(..., description="Total time spent learning (minutes)")
    sessions_this_week: int = Field(..., description="Sessions in the last 7 days")
    time_this_week_minutes: int = Field(..., description="Time spent this week (minutes)")
    unique_topics_learned: int = Field(..., description="Number of unique topics completed")
