"""
Message model - Chat messages in conversations
"""

from sqlalchemy import Column, String, ForeignKey, Text, Enum, DateTime, func, JSON
from sqlalchemy.orm import relationship
import enum
import uuid

from app.database import Base


class MessageRole(str, enum.Enum):
    """Message role enumeration"""
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    """Message model - chat messages"""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)  # Array of source references (NCERT page numbers, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role})>"
