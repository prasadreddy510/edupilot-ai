"""
Worksheet model - Generated practice sheets
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum, DateTime, func, JSON
from sqlalchemy.orm import relationship
import enum
import uuid

from app.database import Base


class DifficultyLevel(str, enum.Enum):
    """Difficulty level enumeration"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Worksheet(Base):
    """Worksheet model - generated practice sheets"""
    __tablename__ = "worksheets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    questions = Column(JSON, nullable=False)  # Array of question objects
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    total_points = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    student = relationship("Student", back_populates="worksheets")
    topic = relationship("Topic", back_populates="worksheets")
    submissions = relationship("WorksheetSubmission", back_populates="worksheet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Worksheet(id={self.id}, title={self.title})>"
