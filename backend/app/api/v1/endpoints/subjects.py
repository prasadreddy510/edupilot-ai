"""
Subjects API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.core.deps import get_db, get_current_user
from app.models import Subject, User
from app.schemas.subject import SubjectResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=List[SubjectResponse])
def list_subjects(
    grade: Optional[int] = Query(None, ge=3, le=10, description="Filter by grade"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all subjects with optional grade filtering

    - Returns all subjects if no grade specified
    - Returns subjects for specific grade if grade provided
    - Requires authentication
    """
    query = db.query(Subject)

    if grade:
        query = query.filter(Subject.grade == grade)

    subjects = query.order_by(Subject.grade, Subject.name).all()

    return [SubjectResponse.model_validate(subject) for subject in subjects]


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject(
    subject_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get subject by ID

    - Returns subject details
    - Requires authentication
    """
    subject = db.query(Subject).filter(Subject.id == subject_id).first()

    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )

    return SubjectResponse.model_validate(subject)
