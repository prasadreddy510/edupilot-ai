"""
User model for authentication
"""

from sqlalchemy import Column, String, Enum, DateTime, func
from sqlalchemy.orm import relationship
import enum
import uuid

from app.database import Base


class UserType(str, enum.Enum):
    """User type enumeration"""
    STUDENT = "student"
    PARENT = "parent"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone_number = Column(String(15), unique=True, nullable=False, index=True)
    user_type = Column(Enum(UserType), nullable=False)
    is_active = Column(String(1), default="1")  # '1' = active, '0' = inactive
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="user", uselist=False, cascade="all, delete-orphan")
    parent = relationship("Parent", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, phone={self.phone_number}, type={self.user_type})>"
