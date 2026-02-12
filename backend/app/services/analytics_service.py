"""
Analytics Service - Progress tracking and weak area detection

Features:
- Mastery level calculation
- Weak area identification
- Performance analytics
- Personalized recommendations
- Progress aggregation
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
import logging

from app.models.student import Student
from app.models.topic import Topic
from app.models.learning_session import LearningSession
from app.models.worksheet_submission import WorksheetSubmission
from app.models.quiz_attempt import QuizAttempt
from app.models.progress_record import ProgressRecord
from app.models.weak_area import WeakArea

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for calculating and analyzing student progress"""

    # Mastery level thresholds
    MASTERY_THRESHOLDS = {
        "beginner": 0,      # 0-30%
        "learning": 30,     # 30-60%
        "proficient": 60,   # 60-85%
        "mastered": 85,     # 85-100%
    }

    def calculate_mastery_level(
        self,
        db: Session,
        student_id: str,
        topic_id: str,
    ) -> Dict[str, Any]:
        """
        Calculate mastery level for a topic

        Formula:
        mastery = (quiz_score × 0.4) + (worksheet_score × 0.3) +
                  (consistency × 0.2) + (retention × 0.1)

        Args:
            db: Database session
            student_id: Student ID
            topic_id: Topic ID

        Returns:
            Mastery data with level and score
        """
        try:
            # Get quiz performance
            quiz_attempts = (
                db.query(QuizAttempt)
                .join(QuizAttempt.quiz)
                .filter(
                    QuizAttempt.student_id == student_id,
                    QuizAttempt.quiz.has(topic_id=topic_id),
                    QuizAttempt.submitted_at.isnot(None),
                )
                .all()
            )

            avg_quiz_score = 0
            if quiz_attempts:
                scores = [a.percentage for a in quiz_attempts if a.percentage is not None]
                avg_quiz_score = sum(scores) / len(scores) if scores else 0

            # Get worksheet performance
            worksheet_submissions = (
                db.query(WorksheetSubmission)
                .join(WorksheetSubmission.worksheet)
                .filter(
                    WorksheetSubmission.student_id == student_id,
                    WorksheetSubmission.worksheet.has(topic_id=topic_id),
                )
                .all()
            )

            avg_worksheet_score = 0
            if worksheet_submissions:
                scores = [s.percentage for s in worksheet_submissions if s.percentage is not None]
                avg_worksheet_score = sum(scores) / len(scores) if scores else 0

            # Calculate consistency (study frequency)
            learning_sessions = (
                db.query(LearningSession)
                .filter(
                    LearningSession.student_id == student_id,
                    LearningSession.topic_id == topic_id,
                )
                .all()
            )

            consistency_score = 0
            if learning_sessions:
                # Check sessions in last 30 days
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                recent_sessions = [
                    s for s in learning_sessions
                    if s.created_at >= thirty_days_ago
                ]
                # Score based on frequency (1 session per week = 100%)
                sessions_per_week = len(recent_sessions) / 4
                consistency_score = min(sessions_per_week * 25, 100)

            # Calculate retention (improvement over time)
            retention_score = 0
            if len(quiz_attempts) >= 2:
                # Compare first and last attempts
                first_score = quiz_attempts[0].percentage or 0
                last_score = quiz_attempts[-1].percentage or 0
                improvement = last_score - first_score
                retention_score = min(max(improvement + 50, 0), 100)  # Normalize to 0-100
            else:
                retention_score = 50  # Neutral if not enough data

            # Calculate weighted mastery
            mastery_score = (
                avg_quiz_score * 0.4 +
                avg_worksheet_score * 0.3 +
                consistency_score * 0.2 +
                retention_score * 0.1
            )

            # Determine mastery level
            mastery_level = "beginner"
            for level, threshold in sorted(
                self.MASTERY_THRESHOLDS.items(),
                key=lambda x: x[1],
                reverse=True
            ):
                if mastery_score >= threshold:
                    mastery_level = level
                    break

            return {
                "topic_id": topic_id,
                "mastery_score": round(mastery_score, 2),
                "mastery_level": mastery_level,
                "components": {
                    "quiz_score": round(avg_quiz_score, 2),
                    "worksheet_score": round(avg_worksheet_score, 2),
                    "consistency": round(consistency_score, 2),
                    "retention": round(retention_score, 2),
                },
                "attempts": {
                    "quizzes": len(quiz_attempts),
                    "worksheets": len(worksheet_submissions),
                    "sessions": len(learning_sessions),
                },
            }

        except Exception as e:
            logger.error(f"Error calculating mastery level: {e}")
            return {
                "topic_id": topic_id,
                "mastery_score": 0,
                "mastery_level": "beginner",
                "error": str(e),
            }

    def update_progress_record(
        self,
        db: Session,
        student_id: str,
        topic_id: str,
    ) -> ProgressRecord:
        """
        Update or create progress record for a topic

        Args:
            db: Database session
            student_id: Student ID
            topic_id: Topic ID

        Returns:
            Updated progress record
        """
        # Calculate mastery
        mastery_data = self.calculate_mastery_level(db, student_id, topic_id)

        # Find or create progress record
        progress = (
            db.query(ProgressRecord)
            .filter(
                ProgressRecord.student_id == student_id,
                ProgressRecord.topic_id == topic_id,
            )
            .first()
        )

        if not progress:
            import uuid
            progress = ProgressRecord(
                id=str(uuid.uuid4()),
                student_id=student_id,
                topic_id=topic_id,
            )
            db.add(progress)

        # Update progress
        progress.mastery_level = mastery_data["mastery_score"]
        progress.average_quiz_score = mastery_data["components"]["quiz_score"]
        progress.average_worksheet_score = mastery_data["components"]["worksheet_score"]
        progress.last_practiced_at = datetime.utcnow()

        db.commit()
        db.refresh(progress)

        return progress

    def identify_weak_areas(
        self,
        db: Session,
        student_id: str,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Identify weak areas (topics needing improvement)

        Criteria:
        - Low mastery score (<60%)
        - Recent failures (quiz/worksheet scores <70%)
        - Inconsistent practice
        - Declining performance

        Args:
            db: Database session
            student_id: Student ID
            limit: Maximum weak areas to return

        Returns:
            List of weak areas with reasons
        """
        try:
            weak_areas = []

            # Get all topics the student has attempted
            progress_records = (
                db.query(ProgressRecord)
                .filter(ProgressRecord.student_id == student_id)
                .all()
            )

            for progress in progress_records:
                # Recalculate mastery
                mastery_data = self.calculate_mastery_level(
                    db, student_id, progress.topic_id
                )

                # Check if weak (mastery < 60%)
                if mastery_data["mastery_score"] < 60:
                    # Determine specific weaknesses
                    reasons = []

                    if mastery_data["components"]["quiz_score"] < 70:
                        reasons.append("Low quiz performance")

                    if mastery_data["components"]["worksheet_score"] < 70:
                        reasons.append("Struggling with practice exercises")

                    if mastery_data["components"]["consistency"] < 50:
                        reasons.append("Irregular practice")

                    if mastery_data["components"]["retention"] < 50:
                        reasons.append("Declining performance over time")

                    weak_areas.append({
                        "topic_id": progress.topic_id,
                        "topic_name": progress.topic.name if progress.topic else "Unknown",
                        "subject": progress.topic.subject.name if progress.topic and progress.topic.subject else None,
                        "mastery_score": mastery_data["mastery_score"],
                        "reasons": reasons,
                        "priority": self._calculate_priority(mastery_data),
                    })

            # Sort by priority (lowest mastery = highest priority)
            weak_areas.sort(key=lambda x: x["priority"], reverse=True)

            return weak_areas[:limit]

        except Exception as e:
            logger.error(f"Error identifying weak areas: {e}")
            return []

    def _calculate_priority(self, mastery_data: Dict[str, Any]) -> int:
        """
        Calculate priority score for weak area

        Higher score = higher priority

        Args:
            mastery_data: Mastery calculation data

        Returns:
            Priority score (0-100)
        """
        # Lower mastery = higher priority
        mastery_priority = 100 - mastery_data["mastery_score"]

        # Recent attempts = higher priority
        attempts_priority = min(
            mastery_data["attempts"]["quizzes"] +
            mastery_data["attempts"]["worksheets"],
            10
        ) * 5

        return int(mastery_priority + attempts_priority)

    def get_student_analytics(
        self,
        db: Session,
        student_id: str,
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics for a student

        Args:
            db: Database session
            student_id: Student ID

        Returns:
            Analytics data
        """
        try:
            # Get total learning time
            total_time = (
                db.query(func.sum(LearningSession.duration_minutes))
                .filter(
                    LearningSession.student_id == student_id,
                    LearningSession.duration_minutes.isnot(None),
                )
                .scalar()
                or 0
            )

            # Get topics studied
            topics_studied = (
                db.query(func.count(func.distinct(LearningSession.topic_id)))
                .filter(LearningSession.student_id == student_id)
                .scalar()
                or 0
            )

            # Get completed topics
            topics_completed = (
                db.query(func.count(ProgressRecord.id))
                .filter(
                    ProgressRecord.student_id == student_id,
                    ProgressRecord.completed == True,
                )
                .scalar()
                or 0
            )

            # Get average quiz score
            avg_quiz_score = (
                db.query(func.avg(QuizAttempt.percentage))
                .filter(
                    QuizAttempt.student_id == student_id,
                    QuizAttempt.submitted_at.isnot(None),
                )
                .scalar()
                or 0
            )

            # Get average worksheet score
            avg_worksheet_score = (
                db.query(func.avg(WorksheetSubmission.percentage))
                .filter(WorksheetSubmission.student_id == student_id)
                .scalar()
                or 0
            )

            # Get weekly stats (last 7 days)
            week_ago = datetime.utcnow() - timedelta(days=7)

            weekly_time = (
                db.query(func.sum(LearningSession.duration_minutes))
                .filter(
                    LearningSession.student_id == student_id,
                    LearningSession.start_time >= week_ago,
                    LearningSession.duration_minutes.isnot(None),
                )
                .scalar()
                or 0
            )

            weekly_sessions = (
                db.query(func.count(LearningSession.id))
                .filter(
                    LearningSession.student_id == student_id,
                    LearningSession.start_time >= week_ago,
                )
                .scalar()
                or 0
            )

            return {
                "total_learning_time_minutes": total_time,
                "topics_studied": topics_studied,
                "topics_completed": topics_completed,
                "average_quiz_score": round(avg_quiz_score, 2),
                "average_worksheet_score": round(avg_worksheet_score, 2),
                "weekly_time_minutes": weekly_time,
                "weekly_sessions": weekly_sessions,
                "overall_progress": round(
                    (topics_completed / max(topics_studied, 1)) * 100, 2
                ),
            }

        except Exception as e:
            logger.error(f"Error getting student analytics: {e}")
            return {}

    def get_subject_breakdown(
        self,
        db: Session,
        student_id: str,
    ) -> List[Dict[str, Any]]:
        """
        Get progress breakdown by subject

        Args:
            db: Database session
            student_id: Student ID

        Returns:
            Subject-wise progress data
        """
        try:
            # Get all progress records
            progress_records = (
                db.query(ProgressRecord)
                .filter(ProgressRecord.student_id == student_id)
                .all()
            )

            # Group by subject
            subject_data = {}
            for progress in progress_records:
                if not progress.topic or not progress.topic.subject:
                    continue

                subject_name = progress.topic.subject.name
                if subject_name not in subject_data:
                    subject_data[subject_name] = {
                        "subject": subject_name,
                        "topics_studied": 0,
                        "topics_mastered": 0,
                        "total_mastery": 0,
                    }

                subject_data[subject_name]["topics_studied"] += 1
                if progress.completed:
                    subject_data[subject_name]["topics_mastered"] += 1
                subject_data[subject_name]["total_mastery"] += progress.mastery_level

            # Calculate averages
            result = []
            for subject_name, data in subject_data.items():
                avg_mastery = (
                    data["total_mastery"] / data["topics_studied"]
                    if data["topics_studied"] > 0
                    else 0
                )
                result.append({
                    "subject": subject_name,
                    "topics_studied": data["topics_studied"],
                    "topics_mastered": data["topics_mastered"],
                    "average_mastery": round(avg_mastery, 2),
                    "progress_percentage": round(
                        (data["topics_mastered"] / max(data["topics_studied"], 1)) * 100, 2
                    ),
                })

            return result

        except Exception as e:
            logger.error(f"Error getting subject breakdown: {e}")
            return []


# Singleton instance
analytics_service = AnalyticsService()
