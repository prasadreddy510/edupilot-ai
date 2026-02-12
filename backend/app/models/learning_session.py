"""
Learning Session model - Time tracking for student learning
"""

from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class LearningSession(Base):
    """Learning session model - tracks time spent on topics"""
    __tablename__ = "learning_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=True)
    duration_minutes = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="learning_sessions")
    topic = relationship("Topic", back_populates="learning_sessions")

    def __repr__(self):
        return f"<LearningSession(id={self.id}, student_id={self.student_id}, topic_id={self.topic_id})>"
