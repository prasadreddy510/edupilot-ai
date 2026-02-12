from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.deps import get_db, get_current_student
from app.models.user import User
from app.models.student import Student
from app.models.topic import Topic
from app.models.quiz import Quiz
from app.models.quiz_attempt import QuizAttempt
from app.schemas.quiz import (
    QuizGenerateRequest,
    QuizResponse,
    QuizAttemptStart,
    QuizAttemptResponse,
    QuizSubmitRequest,
    QuizListResponse,
    QuizStatsResponse,
)
from app.services.quiz_service import quiz_service
import uuid

router = APIRouter()


@router.post("/generate", response_model=QuizResponse)
def generate_quiz(
    request: QuizGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Generate a new quiz for a topic

    - 100% AI-generated questions for variety
    - Timed based on question count
    - Randomized question order
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

    # Generate quiz using service
    quiz_data = quiz_service.generate_quiz(
        topic_id=topic.id,
        topic_name=topic.name,
        subject=topic.subject.name if topic.subject else "General",
        grade=student.grade,
        num_questions=request.num_questions,
        difficulty=request.difficulty,
    )

    # Save quiz to database
    quiz = Quiz(
        id=str(uuid.uuid4()),
        student_id=student.id,
        topic_id=topic.id,
        title=f"{topic.name} - {request.difficulty.capitalize()} Quiz",
        difficulty=request.difficulty,
        total_questions=quiz_data["total_questions"],
        duration_minutes=quiz_data["duration_minutes"],
        max_score=quiz_data["max_score"],
        questions=quiz_data["questions"],
    )

    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return quiz


@router.get("", response_model=List[QuizListResponse])
def list_quizzes(
    topic_id: Optional[str] = Query(None, description="Filter by topic ID"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get all quizzes for the current student
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    query = db.query(Quiz).filter(Quiz.student_id == student.id)

    if topic_id:
        query = query.filter(Quiz.topic_id == topic_id)

    quizzes = query.order_by(desc(Quiz.created_at)).limit(limit).all()

    # Enrich with topic name and attempt stats
    result = []
    for quiz in quizzes:
        # Get all attempts
        attempts = (
            db.query(QuizAttempt)
            .filter(QuizAttempt.quiz_id == quiz.id)
            .order_by(desc(QuizAttempt.submitted_at))
            .all()
        )

        best_score = max([a.percentage for a in attempts]) if attempts else None
        total_attempts = len(attempts)
        latest_attempt = attempts[0] if attempts else None

        result.append(
            QuizListResponse(
                id=quiz.id,
                title=quiz.title,
                topic_id=quiz.topic_id,
                topic_name=quiz.topic.name if quiz.topic else "Unknown",
                difficulty=quiz.difficulty,
                total_questions=quiz.total_questions,
                duration_minutes=quiz.duration_minutes,
                max_score=quiz.max_score,
                created_at=quiz.created_at,
                total_attempts=total_attempts,
                best_score=best_score,
                latest_score=latest_attempt.percentage if latest_attempt else None,
            )
        )

    return result


@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(
    quiz_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get a specific quiz by ID
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    quiz = (
        db.query(Quiz)
        .filter(
            Quiz.id == quiz_id,
            Quiz.student_id == student.id,
        )
        .first()
    )

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    return quiz


@router.post("/{quiz_id}/start", response_model=QuizAttemptResponse)
def start_quiz_attempt(
    quiz_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Start a new quiz attempt

    Records start time for timer tracking
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Get quiz
    quiz = (
        db.query(Quiz)
        .filter(
            Quiz.id == quiz_id,
            Quiz.student_id == student.id,
        )
        .first()
    )

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    # Check for active attempt
    active_attempt = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.student_id == student.id,
            QuizAttempt.submitted_at.is_(None),
        )
        .first()
    )

    if active_attempt:
        # Return existing active attempt
        return active_attempt

    # Create new attempt
    attempt = QuizAttempt(
        id=str(uuid.uuid4()),
        quiz_id=quiz.id,
        student_id=student.id,
        started_at=datetime.utcnow(),
        answers={},
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    return attempt


@router.post("/{quiz_id}/submit", response_model=QuizAttemptResponse)
def submit_quiz(
    quiz_id: str,
    submission: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Submit quiz answers and get grading results

    Includes time tracking and improvement analysis
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Get quiz
    quiz = (
        db.query(Quiz)
        .filter(
            Quiz.id == quiz_id,
            Quiz.student_id == student.id,
        )
        .first()
    )

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    # Get active attempt
    attempt = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.student_id == student.id,
            QuizAttempt.id == submission.attempt_id,
        )
        .first()
    )

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz attempt not found",
        )

    if attempt.submitted_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quiz already submitted",
        )

    # Calculate time taken
    time_taken_seconds = int((datetime.utcnow() - attempt.started_at).total_seconds())

    # Grade the quiz
    grading_result = quiz_service.grade_quiz(
        questions=quiz.questions,
        student_answers=submission.answers,
        time_taken_seconds=time_taken_seconds,
        duration_minutes=quiz.duration_minutes,
    )

    # Get previous attempts for improvement calculation
    previous_attempts = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.student_id == student.id,
            QuizAttempt.submitted_at.isnot(None),
            QuizAttempt.id != attempt.id,
        )
        .order_by(QuizAttempt.submitted_at)
        .all()
    )

    previous_scores = [a.percentage for a in previous_attempts]
    improvement_stats = quiz_service.calculate_improvement(
        current_score=grading_result["percentage"],
        previous_scores=previous_scores,
    )

    # Update attempt with results
    attempt.submitted_at = datetime.utcnow()
    attempt.answers = submission.answers
    attempt.score = grading_result["total_score"]
    attempt.max_score = grading_result["max_score"]
    attempt.percentage = grading_result["percentage"]
    attempt.graded_answers = grading_result["graded_answers"]
    attempt.passed = grading_result["passed"]
    attempt.time_taken_seconds = grading_result["time_taken_seconds"]
    attempt.time_exceeded = grading_result["time_exceeded"]
    attempt.improvement_data = improvement_stats

    db.commit()
    db.refresh(attempt)

    return attempt


@router.get("/{quiz_id}/attempts", response_model=List[QuizAttemptResponse])
def get_quiz_attempts(
    quiz_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get all attempts for a quiz
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Verify quiz ownership
    quiz = (
        db.query(Quiz)
        .filter(
            Quiz.id == quiz_id,
            Quiz.student_id == student.id,
        )
        .first()
    )

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    attempts = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.submitted_at.isnot(None),  # Only completed attempts
        )
        .order_by(desc(QuizAttempt.submitted_at))
        .all()
    )

    return attempts


@router.get("/{quiz_id}/stats", response_model=QuizStatsResponse)
def get_quiz_stats(
    quiz_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    """
    Get statistics for a quiz across all attempts
    """
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )

    # Verify quiz ownership
    quiz = (
        db.query(Quiz)
        .filter(
            Quiz.id == quiz_id,
            Quiz.student_id == student.id,
        )
        .first()
    )

    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found",
        )

    # Get all completed attempts
    attempts = (
        db.query(QuizAttempt)
        .filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.submitted_at.isnot(None),
        )
        .order_by(QuizAttempt.submitted_at)
        .all()
    )

    if not attempts:
        return QuizStatsResponse(
            quiz_id=quiz_id,
            total_attempts=0,
            best_score=0,
            average_score=0,
            latest_score=0,
            improvement_trend=0,
            average_time_seconds=0,
        )

    scores = [a.percentage for a in attempts]
    times = [a.time_taken_seconds for a in attempts if a.time_taken_seconds]

    # Calculate improvement trend (first vs last)
    improvement_trend = scores[-1] - scores[0] if len(scores) > 1 else 0

    return QuizStatsResponse(
        quiz_id=quiz_id,
        total_attempts=len(attempts),
        best_score=round(max(scores), 2),
        average_score=round(sum(scores) / len(scores), 2),
        latest_score=round(scores[-1], 2),
        improvement_trend=round(improvement_trend, 2),
        average_time_seconds=round(sum(times) / len(times), 0) if times else 0,
    )
