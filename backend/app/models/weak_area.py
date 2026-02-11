"""
Weak Area model - AI-identified weak topics
"""

from sqlalchemy import Column, String, Float, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class WeakArea(Base):
    """Weak area model - AI-identified weak topics"""
    __tablename__ = "weak_areas"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    mastery_level = Column(Float, default=0.0)  # Current mastery level (0-100)
    identified_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="weak_areas")
    topic = relationship("Topic", back_populates="weak_areas")

    def __repr__(self):
        return f"<WeakArea(id={self.id}, mastery={self.mastery_level}%)>"
