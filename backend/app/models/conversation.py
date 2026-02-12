"""
Conversation model - Doubt chat threads
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
import uuid

from app.database import Base


class Conversation(Base):
    """Conversation model - doubt chat threads"""
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    student_id = Column(String(36), ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=False)
    subject = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    student = relationship("Student", back_populates="conversations")
    topic = relationship("Topic", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, title={self.title})>"
