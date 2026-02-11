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
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, default=30)  # Quiz duration
    questions = Column(JSON, nullable=False)  # Array of question objects
    total_points = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    topic = relationship("Topic", back_populates="quizzes")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Quiz(id={self.id}, title={self.title})>"
