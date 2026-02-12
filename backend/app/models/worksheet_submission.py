"""
Worksheet Submission model - Student answers and scores
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, func, JSON
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class WorksheetSubmission(Base):
    """Worksheet submission model - student answers and grades"""
    __tablename__ = "worksheet_submissions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    worksheet_id = Column(String(36), ForeignKey("worksheets.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    answers = Column(JSON, nullable=False)  # Dict of question_id: answer
    score = Column(Float, default=0)  # Points earned
    max_score = Column(Integer, default=0)  # Total possible points
    percentage = Column(Float, default=0.0)
    graded_answers = Column(JSON, nullable=True)  # List of graded answer objects
    passed = Column(Boolean, default=False)
    feedback = Column(JSON, nullable=True)  # Dict of question_id: feedback
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    graded_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    worksheet = relationship("Worksheet", back_populates="submissions")
    student = relationship("Student", back_populates="worksheet_submissions")

    def __repr__(self):
        return f"<WorksheetSubmission(id={self.id}, score={self.score}/{self.max_score})>"
