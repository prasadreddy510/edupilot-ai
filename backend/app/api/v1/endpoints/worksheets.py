from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.deps import get_db, get_current_student
from app.models.user import User
from app.models.student import Student
from app.models.topic import Topic
from app.models.worksheet import Worksheet, WorksheetSubmission
from app.schemas.worksheet import (
    WorksheetGenerateRequest,
    WorksheetResponse,
    WorksheetSubmitRequest,
    WorksheetSubmissionResponse,
    WorksheetListResponse,
)
from app.services.worksheet_service import worksheet_service
import uuid

router = APIRouter()


@router.post("/generate", response_model=WorksheetResponse)
def generate_worksheet(
    request: WorksheetGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Generate a new worksheet for a topic

    Uses hybrid approach:
    - 70% template-based questions (fast, consistent)
    - 30% AI-generated questions (variety, creativity)
    """
    # Verify topic exists
    topic = db.query(Topic).filter(Topic.id == request.topic_id).first()
    if not topic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Topic not found",
        )

    # Get student
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Generate worksheet using service
    worksheet_data = worksheet_service.generate_worksheet(
        topic_id=topic.id,
        topic_name=topic.name,
        subject=topic.subject.name if topic.subject else "General",
        grade=student.grade,
        num_questions=request.num_questions,
        difficulty=request.difficulty,
    )

    # Save worksheet to database
    worksheet = Worksheet(
        id=str(uuid.uuid4()),
        student_id=student.id,
        topic_id=topic.id,
        title=f"{topic.name} - {request.difficulty.capitalize()} Worksheet",
        difficulty=request.difficulty,
        total_questions=worksheet_data["total_questions"],
        max_score=worksheet_data["max_score"],
        questions=worksheet_data["questions"],
    )

    db.add(worksheet)
    db.commit()
    db.refresh(worksheet)

    return worksheet


@router.get("", response_model=List[WorksheetListResponse])
def list_worksheets(
    topic_id: Optional[str] = Query(None, description="Filter by topic ID"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get all worksheets for the current student
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    query = db.query(Worksheet).filter(Worksheet.student_id == student.id)

    if topic_id:
        query = query.filter(Worksheet.topic_id == topic_id)

    worksheets = query.order_by(desc(Worksheet.created_at)).limit(limit).all()

    # Enrich with topic name and submission status
    result = []
    for worksheet in worksheets:
        # Get latest submission
        submission = (
            db.query(WorksheetSubmission)
            .filter(WorksheetSubmission.worksheet_id == worksheet.id)
            .order_by(desc(WorksheetSubmission.submitted_at))
            .first()
        )

        result.append(
            WorksheetListResponse(
                id=worksheet.id,
                title=worksheet.title,
                topic_id=worksheet.topic_id,
                topic_name=worksheet.topic.name if worksheet.topic else "Unknown",
                difficulty=worksheet.difficulty,
                total_questions=worksheet.total_questions,
                max_score=worksheet.max_score,
                created_at=worksheet.created_at,
                is_submitted=submission is not None,
                latest_score=submission.score if submission else None,
                latest_percentage=submission.percentage if submission else None,
            )
        )

    return result


@router.get("/{worksheet_id}", response_model=WorksheetResponse)
def get_worksheet(
    worksheet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get a specific worksheet by ID
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    worksheet = (
        db.query(Worksheet)
        .filter(
            Worksheet.id == worksheet_id,
            Worksheet.student_id == student.id,
        )
        .first()
    )

    if not worksheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worksheet not found",
        )

    return worksheet


@router.post("/{worksheet_id}/submit", response_model=WorksheetSubmissionResponse)
def submit_worksheet(
    worksheet_id: str,
    submission: WorksheetSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Submit answers for a worksheet and get grading results

    Uses multi-tier grading:
    - Tier 1: Deterministic (MCQ, True/False)
    - Tier 2: Pattern-based (Numerical)
    - Tier 3: AI-based (Short Answer)
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Get worksheet
    worksheet = (
        db.query(Worksheet)
        .filter(
            Worksheet.id == worksheet_id,
            Worksheet.student_id == student.id,
        )
        .first()
    )

    if not worksheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worksheet not found",
        )

    # Grade the worksheet
    grading_result = worksheet_service.grade_worksheet(
        questions=worksheet.questions,
        student_answers=submission.answers,
    )

    # Save submission
    worksheet_submission = WorksheetSubmission(
        id=str(uuid.uuid4()),
        worksheet_id=worksheet.id,
        student_id=student.id,
        answers=submission.answers,
        score=grading_result["total_score"],
        max_score=grading_result["max_score"],
        percentage=grading_result["percentage"],
        graded_answers=grading_result["graded_answers"],
        passed=grading_result["passed"],
        submitted_at=datetime.utcnow(),
    )

    db.add(worksheet_submission)
    db.commit()
    db.refresh(worksheet_submission)

    return worksheet_submission


@router.get("/{worksheet_id}/submissions", response_model=List[WorksheetSubmissionResponse])
def get_worksheet_submissions(
    worksheet_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get all submissions for a worksheet
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Verify worksheet ownership
    worksheet = (
        db.query(Worksheet)
        .filter(
            Worksheet.id == worksheet_id,
            Worksheet.student_id == student.id,
        )
        .first()
    )

    if not worksheet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Worksheet not found",
        )

    submissions = (
        db.query(WorksheetSubmission)
        .filter(WorksheetSubmission.worksheet_id == worksheet_id)
        .order_by(desc(WorksheetSubmission.submitted_at))
        .all()
    )

    return submissions


@router.get("/submissions/latest", response_model=List[WorksheetSubmissionResponse])
def get_latest_submissions(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get latest worksheet submissions for the student
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    submissions = (
        db.query(WorksheetSubmission)
        .filter(WorksheetSubmission.student_id == student.id)
        .order_by(desc(WorksheetSubmission.submitted_at))
        .limit(limit)
        .all()
    )

    return submissions
