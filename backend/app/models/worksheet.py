"""
Worksheet model - Generated practice sheets
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, Text, DateTime, func, JSON
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Worksheet(Base):
    """Worksheet model - generated practice sheets"""
    __tablename__ = "worksheets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    questions = Column(JSON, nullable=False)  # Array of question objects
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    total_questions = Column(Integer, default=0)
    max_score = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="worksheets")
    topic = relationship("Topic", back_populates="worksheets")
    submissions = relationship("WorksheetSubmission", back_populates="worksheet", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Worksheet(id={self.id}, title={self.title})>"
