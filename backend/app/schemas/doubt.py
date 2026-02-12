"""
Doubt/Conversation Pydantic schemas
"""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ConversationCreate(BaseModel):
    """Request to create a new conversation"""
    title: str = Field(..., min_length=1, max_length=200, description="Conversation title")
    topic_id: Optional[str] = Field(None, description="Optional topic ID")
    subject: Optional[str] = Field(None, description="Optional subject")


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: str
    student_id: str
    topic_id: Optional[str] = None
    title: str
    subject: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    """Simplified conversation list item"""
    id: str
    student_id: str
    topic_id: Optional[str] = None
    topic_name: Optional[str] = None
    title: str
    subject: Optional[str] = None
    message_count: int
    last_message: Optional[str] = None
    last_message_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    """Request to create a message"""
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")


class MessageResponse(BaseModel):
    """Message response"""
    id: str
    conversation_id: str
    role: str  # 'user' or 'assistant'
    content: str
    extra_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Request to send a chat message"""
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")
    topic: Optional[str] = Field(None, description="Optional topic for context")
    subject: Optional[str] = Field(None, description="Optional subject for context")


class Source(BaseModel):
    """Source attribution"""
    text: str
    metadata: Dict[str, Any]


class ChatResponse(BaseModel):
    """Response with user message and AI response"""
    user_message: MessageResponse
    assistant_message: MessageResponse
    sources: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True
