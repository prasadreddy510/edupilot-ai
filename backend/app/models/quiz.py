"""
Quiz model - Quiz definitions
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Text, DateTime, func, JSON
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Quiz(Base):
    """Quiz model - quiz definitions"""
    __tablename__ = "quizzes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    total_questions = Column(Integer, default=0)
    duration_minutes = Column(Integer, default=30)
    questions = Column(JSON, nullable=False)  # Array of question objects
    max_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    topic = relationship("Topic", back_populates="quizzes")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz(id={self.id}, title={self.title})>"
