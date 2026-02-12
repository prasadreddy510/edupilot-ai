from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_student
from app.models.user import User
from app.models.student import Student
from app.models.progress_record import ProgressRecord
from app.schemas.progress import (
    ProgressRecordResponse,
    MasteryCalculationResponse,
    WeakAreaResponse,
    StudentAnalyticsResponse,
    SubjectBreakdownResponse,
    ProgressUpdateRequest,
)
from app.services.analytics_service import analytics_service
import uuid

router = APIRouter()


@router.get("/analytics", response_model=StudentAnalyticsResponse)
def get_student_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get comprehensive analytics for the current student

    Includes:
    - Total learning time
    - Topics studied and completed
    - Average scores
    - Weekly statistics
    - Overall progress percentage
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    analytics = analytics_service.get_student_analytics(db, student.id)

    return StudentAnalyticsResponse(**analytics)


@router.get("/subject-breakdown", response_model=List[SubjectBreakdownResponse])
def get_subject_breakdown(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get progress breakdown by subject

    Shows performance metrics for each subject
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    breakdown = analytics_service.get_subject_breakdown(db, student.id)

    return [SubjectBreakdownResponse(**item) for item in breakdown]


@router.get("/weak-areas", response_model=List[WeakAreaResponse])
def get_weak_areas(
    limit: int = Query(5, ge=1, le=20, description="Maximum weak areas to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Identify weak areas (topics needing improvement)

    Returns topics with low mastery scores and specific reasons
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    weak_areas = analytics_service.identify_weak_areas(db, student.id, limit)

    return [WeakAreaResponse(**area) for area in weak_areas]


@router.get("/topics/{topic_id}/mastery", response_model=MasteryCalculationResponse)
def get_topic_mastery(
    topic_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Calculate mastery level for a specific topic

    Formula:
    mastery = (quiz_score × 0.4) + (worksheet_score × 0.3) +
              (consistency × 0.2) + (retention × 0.1)
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    mastery_data = analytics_service.calculate_mastery_level(db, student.id, topic_id)

    return MasteryCalculationResponse(**mastery_data)


@router.post("/topics/{topic_id}/update", response_model=ProgressRecordResponse)
def update_topic_progress(
    topic_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Update progress record for a topic

    Recalculates mastery and updates the progress record
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    progress = analytics_service.update_progress_record(db, student.id, topic_id)

    return progress


@router.get("/records", response_model=List[ProgressRecordResponse])
def get_progress_records(
    subject: Optional[str] = Query(None, description="Filter by subject"),
    completed_only: bool = Query(False, description="Show only completed topics"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get all progress records for the student

    Can filter by subject or completion status
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    query = db.query(ProgressRecord).filter(ProgressRecord.student_id == student.id)

    if completed_only:
        query = query.filter(ProgressRecord.mastery_level >= 85.0)

    if subject:
        # Join with topic and subject
        query = query.join(ProgressRecord.topic).filter(
            ProgressRecord.topic.has(subject=subject)
        )

    records = query.order_by(ProgressRecord.last_practiced_at.desc()).all()

    return records
