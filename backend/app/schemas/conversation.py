"""
Conversation and Message Pydantic schemas
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

from app.models.message import MessageRole


class MessageBase(BaseModel):
    """Base message schema"""
    conversation_id: str
    role: MessageRole
    content: str = Field(..., min_length=1)
    sources: Optional[List[str]] = None


class MessageCreate(BaseModel):
    """Schema for creating a message"""
    role: MessageRole
    content: str = Field(..., min_length=1)
    sources: Optional[List[str]] = None


class MessageResponse(MessageBase):
    """Schema for message response"""
    id: str
    created_at: datetime

    class Config:
        from_attributes = True


class ConversationBase(BaseModel):
    """Base conversation schema"""
    student_id: str
    topic_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)


class ConversationCreate(ConversationBase):
    """Schema for creating a conversation"""
    pass


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    topic_id: Optional[str] = None


class ConversationResponse(ConversationBase):
    """Schema for conversation response"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationWithMessages(ConversationResponse):
    """Schema for conversation with messages"""
    messages: List[MessageResponse] = []

    class Config:
        from_attributes = True
