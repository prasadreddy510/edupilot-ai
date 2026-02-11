"""
Topic model - Learning concepts within subjects
"""

from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Topic(Base):
    """Topic model - Learning concepts within subjects"""
    __tablename__ = "topics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String(36), ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)  # e.g., "Fractions", "Photosynthesis"
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)  # Order within subject
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    subject = relationship("Subject", back_populates="topics")
    learning_sessions = relationship("LearningSession", back_populates="topic", cascade="all, delete-orphan")
    worksheets = relationship("Worksheet", back_populates="topic", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="topic", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="topic")
    progress_records = relationship("ProgressRecord", back_populates="topic", cascade="all, delete-orphan")
    weak_areas = relationship("WeakArea", back_populates="topic", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Topic(id={self.id}, name={self.name})>"
