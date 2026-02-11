"""
Parent-Student relationship model
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, func, Enum
from sqlalchemy.orm import relationship
import enum
import uuid

from app.database import Base


class RelationshipType(str, enum.Enum):
    """Relationship type enumeration"""
    MOTHER = "mother"
    FATHER = "father"
    GUARDIAN = "guardian"


class ParentStudentLink(Base):
    """Link between parents and students"""
    __tablename__ = "parent_student_links"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    parent_id = Column(String(36), ForeignKey("parents.id", ondelete="CASCADE"), nullable=False)
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    relationship_type = Column(Enum(RelationshipType), default=RelationshipType.GUARDIAN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    parent = relationship("Parent", back_populates="student_links")
    student = relationship("Student", back_populates="parent_links")

    def __repr__(self):
        return f"<ParentStudentLink(parent_id={self.parent_id}, student_id={self.student_id})>"
