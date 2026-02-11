"""
Subject model - NCERT subjects by grade
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Subject(Base):
    """Subject model - NCERT subjects by grade"""
    __tablename__ = "subjects"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)  # e.g., "Mathematics", "Science"
    grade = Column(Integer, nullable=False)  # 3-10
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)  # Icon name for frontend
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    topics = relationship("Topic", back_populates="subject", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Subject(id={self.id}, name={self.name}, grade={self.grade})>"
