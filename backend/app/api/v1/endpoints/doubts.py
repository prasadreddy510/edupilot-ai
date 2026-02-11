from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_

from app.core.deps import get_db, get_current_student
from app.models.user import User
from app.models.student import Student
from app.models.conversation import Conversation
from app.models.message import Message
from app.schemas.doubt import (
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    MessageCreate,
    MessageResponse,
    ChatRequest,
    ChatResponse,
)
from app.services.chatbot_service import chatbot_service
import uuid

router = APIRouter()


@router.post("/conversations", response_model=ConversationResponse)
def create_conversation(
    conversation_data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Create a new conversation thread

    Optionally linked to a specific topic
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Create conversation
    conversation = Conversation(
        id=str(uuid.uuid4()),
        student_id=student.id,
        topic_id=conversation_data.topic_id,
        title=conversation_data.title,
        subject=conversation_data.subject,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get("/conversations", response_model=List[ConversationListResponse])
def list_conversations(
    topic_id: Optional[str] = Query(None, description="Filter by topic ID"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    search: Optional[str] = Query(None, description="Search in title"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get all conversations for the current student
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    query = db.query(Conversation).filter(Conversation.student_id == student.id)

    if topic_id:
        query = query.filter(Conversation.topic_id == topic_id)

    if subject:
        query = query.filter(Conversation.subject == subject)

    if search:
        query = query.filter(Conversation.title.ilike(f"%{search}%"))

    conversations = query.order_by(desc(Conversation.updated_at)).limit(limit).all()

    # Enrich with message counts and last message
    result = []
    for conv in conversations:
        message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()

        last_message = (
            db.query(Message)
            .filter(Message.conversation_id == conv.id)
            .order_by(desc(Message.created_at))
            .first()
        )

        result.append(
            ConversationListResponse(
                id=conv.id,
                student_id=conv.student_id,
                topic_id=conv.topic_id,
                topic_name=conv.topic.name if conv.topic else None,
                title=conv.title,
                subject=conv.subject,
                message_count=message_count,
                last_message=last_message.content[:100] + "..." if last_message and len(last_message.content) > 100 else last_message.content if last_message else None,
                last_message_at=last_message.created_at if last_message else None,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
            )
        )

    return result


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get a specific conversation by ID
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.student_id == student.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get all messages in a conversation
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Verify conversation ownership
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.student_id == student.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(limit)
        .all()
    )

    return messages


@router.post("/conversations/{conversation_id}/messages", response_model=ChatResponse)
def send_message(
    conversation_id: str,
    message_data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Send a message and get AI response

    This is the main chatbot endpoint:
    1. Validates student's message
    2. Saves student's message
    3. Gets conversation history
    4. Generates AI response with RAG
    5. Saves AI response
    6. Returns both messages
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Verify conversation ownership
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.student_id == student.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Validate message
    validation = chatbot_service.validate_message(message_data.content)
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation["error"],
        )

    # Save student's message
    student_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="user",
        content=message_data.content,
    )
    db.add(student_message)

    # Get conversation history (last 10 messages)
    previous_messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .limit(10)
        .all()
    )

    # Format history for AI
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in previous_messages
    ]

    # Add current message
    conversation_history.append({"role": "user", "content": message_data.content})

    # Generate AI response
    ai_result = chatbot_service.generate_response(
        user_message=message_data.content,
        conversation_history=conversation_history,
        student_grade=student.grade,
        topic=conversation.topic.name if conversation.topic else None,
        subject=conversation.subject,
    )

    # Save AI response
    ai_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role="assistant",
        content=ai_result["response"],
        metadata={
            "sources": ai_result["sources"],
            "has_context": ai_result["has_context"],
        },
    )
    db.add(ai_message)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(student_message)
    db.refresh(ai_message)

    return ChatResponse(
        user_message=student_message,
        assistant_message=ai_message,
        sources=ai_result["sources"],
    )


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Delete a conversation and all its messages
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Verify conversation ownership
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.student_id == student.id,
        )
        .first()
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Delete all messages first
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()

    # Delete conversation
    db.delete(conversation)
    db.commit()

    return {"message": "Conversation deleted successfully"}


@router.post("/quick-ask", response_model=ChatResponse)
def quick_ask(
    message_data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Quick ask without creating a conversation

    For one-off questions
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Validate message
    validation = chatbot_service.validate_message(message_data.content)
    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation["error"],
        )

    # Generate AI response (no history)
    ai_result = chatbot_service.generate_response(
        user_message=message_data.content,
        conversation_history=[],
        student_grade=student.grade,
        topic=message_data.topic,
        subject=message_data.subject,
    )

    # Create temporary message objects (not saved)
    from app.models.message import Message as MessageModel

    student_message = MessageModel(
        id=str(uuid.uuid4()),
        conversation_id="quick-ask",
        role="user",
        content=message_data.content,
    )

    ai_message = MessageModel(
        id=str(uuid.uuid4()),
        conversation_id="quick-ask",
        role="assistant",
        content=ai_result["response"],
        metadata={
            "sources": ai_result["sources"],
            "has_context": ai_result["has_context"],
        },
    )

    return ChatResponse(
        user_message=student_message,
        assistant_message=ai_message,
        sources=ai_result["sources"],
    )
