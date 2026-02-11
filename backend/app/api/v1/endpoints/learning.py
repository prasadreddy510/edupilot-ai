from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.deps import get_db, get_current_student
from app.models.user import User
from app.models.student import Student
from app.models.learning_session import LearningSession
from app.schemas.learning import (
    LearningSessionCreate,
    LearningSessionUpdate,
    LearningSessionResponse,
    LearningSessionStats,
)

router = APIRouter()


@router.post("/sessions", response_model=LearningSessionResponse)
def start_learning_session(
    session_data: LearningSessionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Start a new learning session for a topic.
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Check if there's an active session for this topic
    active_session = (
        db.query(LearningSession)
        .filter(
            LearningSession.student_id == student.id,
            LearningSession.topic_id == session_data.topic_id,
            LearningSession.end_time.is_(None),
        )
        .first()
    )

    if active_session:
        # Return the existing active session
        return active_session

    # Create new session
    learning_session = LearningSession(
        student_id=student.id,
        topic_id=session_data.topic_id,
        start_time=datetime.utcnow(),
    )

    db.add(learning_session)
    db.commit()
    db.refresh(learning_session)

    return learning_session


@router.patch("/sessions/{session_id}", response_model=LearningSessionResponse)
def end_learning_session(
    session_id: str,
    session_update: LearningSessionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    End a learning session and calculate duration.
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Get the session
    session = (
        db.query(LearningSession)
        .filter(
            LearningSession.id == session_id,
            LearningSession.student_id == student.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found",
        )

    if session.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already ended",
        )

    # Update session
    session.end_time = datetime.utcnow()
    session.duration_minutes = int(
        (session.end_time - session.start_time).total_seconds() / 60
    )

    if session_update.completed is not None:
        session.completed = session_update.completed

    db.commit()
    db.refresh(session)

    return session


@router.get("/sessions", response_model=List[LearningSessionResponse])
def get_learning_sessions(
    topic_id: str = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get learning sessions for the current student.
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    query = db.query(LearningSession).filter(LearningSession.student_id == student.id)

    if topic_id:
        query = query.filter(LearningSession.topic_id == topic_id)

    sessions = (
        query.order_by(LearningSession.start_time.desc()).limit(limit).all()
    )

    return sessions


@router.get("/sessions/stats", response_model=LearningSessionStats)
def get_learning_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get learning statistics for the current student.
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Total sessions
    total_sessions = (
        db.query(func.count(LearningSession.id))
        .filter(LearningSession.student_id == student.id)
        .scalar()
    )

    # Total time (minutes)
    total_time = (
        db.query(func.sum(LearningSession.duration_minutes))
        .filter(
            LearningSession.student_id == student.id,
            LearningSession.duration_minutes.isnot(None),
        )
        .scalar()
        or 0
    )

    # Sessions this week
    from datetime import timedelta

    week_ago = datetime.utcnow() - timedelta(days=7)
    sessions_this_week = (
        db.query(func.count(LearningSession.id))
        .filter(
            LearningSession.student_id == student.id,
            LearningSession.start_time >= week_ago,
        )
        .scalar()
    )

    # Time this week
    time_this_week = (
        db.query(func.sum(LearningSession.duration_minutes))
        .filter(
            LearningSession.student_id == student.id,
            LearningSession.start_time >= week_ago,
            LearningSession.duration_minutes.isnot(None),
        )
        .scalar()
        or 0
    )

    # Unique topics learned
    unique_topics = (
        db.query(func.count(func.distinct(LearningSession.topic_id)))
        .filter(
            LearningSession.student_id == student.id,
            LearningSession.completed == True,
        )
        .scalar()
    )

    return LearningSessionStats(
        total_sessions=total_sessions,
        total_time_minutes=total_time,
        sessions_this_week=sessions_this_week,
        time_this_week_minutes=time_this_week,
        unique_topics_learned=unique_topics,
    )


@router.get("/sessions/{session_id}", response_model=LearningSessionResponse)
def get_learning_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get a specific learning session.
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    session = (
        db.query(LearningSession)
        .filter(
            LearningSession.id == session_id,
            LearningSession.student_id == student.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learning session not found",
        )

    return session
