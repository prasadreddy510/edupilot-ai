"""
Progress Record model - Mastery tracking
"""

from sqlalchemy import Column, String, Integer, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class ProgressRecord(Base):
    """Progress record model - tracks mastery levels"""
    __tablename__ = "progress_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    mastery_level = Column(Float, default=0.0)  # 0-100
    total_time_spent_seconds = Column(Integer, default=0)
    quiz_count = Column(Integer, default=0)
    worksheet_count = Column(Integer, default=0)
    average_quiz_score = Column(Float, default=0.0)  # 0-100
    average_worksheet_score = Column(Float, default=0.0)  # 0-100
    last_practiced_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="progress_records")
    topic = relationship("Topic", back_populates="progress_records")

    def __repr__(self):
        return f"<ProgressRecord(id={self.id}, mastery={self.mastery_level}%)>"
