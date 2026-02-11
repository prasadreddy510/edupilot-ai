"""
Topics API endpoints with AI-powered explanations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.deps import get_db, get_current_user
from app.models import Topic, Subject, User
from app.schemas.topic import TopicResponse
from app.services.education_service import education_service
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class ExplanationRequest(BaseModel):
    """Request for topic explanation"""
    difficulty: str = "medium"  # easy, medium, hard


class ExplanationResponse(BaseModel):
    """Response with topic explanation"""
    topic_id: str
    topic_name: str
    subject: str
    grade: int
    explanation: str
    difficulty: str


@router.get("", response_model=List[TopicResponse])
def list_topics(
    subject_id: Optional[str] = Query(None, description="Filter by subject ID"),
    grade: Optional[int] = Query(None, ge=3, le=10, description="Filter by grade"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List topics with optional filtering

    - Filter by subject ID
    - Filter by grade
    - Returns all topics if no filters provided
    """
    query = db.query(Topic)

    if subject_id:
        query = query.filter(Topic.subject_id == subject_id)

    if grade:
        # Join with subjects to filter by grade
        query = query.join(Subject).filter(Subject.grade == grade)

    topics = query.order_by(Topic.order).all()

    return [TopicResponse.model_validate(topic) for topic in topics]


@router.get("/{topic_id}", response_model=TopicResponse)
def get_topic(
    topic_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get topic by ID

    - Returns topic details
    - Requires authentication
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    return TopicResponse.model_validate(topic)


@router.post("/{topic_id}/explain", response_model=ExplanationResponse)
def explain_topic(
    topic_id: str,
    request: ExplanationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered explanation for a topic

    - Uses RAG to retrieve relevant NCERT content
    - Generates personalized explanation with Claude AI
    - Caches results for better performance
    - Requires authentication
    """
    # Get topic
    topic = db.query(Topic).filter(Topic.id == topic_id).first()

    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found"
        )

    # Get subject
    subject = db.query(Subject).filter(Subject.id == topic.subject_id).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )

    try:
        # Generate explanation using AI + RAG
        explanation = education_service.explain_topic(
            topic_name=topic.name,
            grade=subject.grade,
            subject=subject.name,
            difficulty=request.difficulty,
            use_cache=True
        )

        return ExplanationResponse(
            topic_id=topic.id,
            topic_name=topic.name,
            subject=subject.name,
            grade=subject.grade,
            explanation=explanation,
            difficulty=request.difficulty
        )

    except Exception as e:
        logger.error(f"Error generating explanation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate explanation"
        )
