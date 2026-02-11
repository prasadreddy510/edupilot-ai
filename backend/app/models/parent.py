"""
Parent model
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Parent(Base):
    """Parent profile model"""
    __tablename__ = "parents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="parent")
    student_links = relationship("ParentStudentLink", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Parent(id={self.id}, name={self.name})>"
