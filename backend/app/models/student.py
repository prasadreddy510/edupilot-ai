"""
Student model
"""

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Student(Base):
    """Student profile model"""
    __tablename__ = "students"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    grade = Column(Integer, nullable=False)  # 3-10
    email = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="student")
    parent_links = relationship("ParentStudentLink", back_populates="student", cascade="all, delete-orphan")
    learning_sessions = relationship("LearningSession", back_populates="student", cascade="all, delete-orphan")
    worksheets = relationship("Worksheet", back_populates="student", cascade="all, delete-orphan")
    worksheet_submissions = relationship("WorksheetSubmission", back_populates="student", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="student", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="student", cascade="all, delete-orphan")
    progress_records = relationship("ProgressRecord", back_populates="student", cascade="all, delete-orphan")
    weak_areas = relationship("WeakArea", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name}, grade={self.grade})>"
