"""
Quiz Attempt model - Quiz history and scores
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class QuizAttempt(Base):
    """Quiz attempt model - quiz history"""
    __tablename__ = "quiz_attempts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    quiz_id = Column(String(36), ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    answers = Column(JSON, nullable=False)  # Dict of question_id: answer
    score = Column(Integer, default=0)  # Points earned
    max_score = Column(Integer, default=0)  # Total possible points
    percentage = Column(Float, nullable=True)
    graded_answers = Column(JSON, nullable=True)  # List of graded answer objects
    passed = Column(Boolean, nullable=True)
    time_taken_seconds = Column(Integer, default=0)
    time_exceeded = Column(Boolean, nullable=True)
    improvement_data = Column(JSON, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("Student", back_populates="quiz_attempts")

    def __repr__(self):
        return f"<QuizAttempt(id={self.id}, score={self.score}/{self.max_score})>"
