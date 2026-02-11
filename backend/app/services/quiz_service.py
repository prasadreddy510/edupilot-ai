"""
Quiz Service - Timed quizzes with auto-grading

Key differences from worksheets:
- Time-limited (configurable duration)
- Auto-submit on timer expiration
- Multiple attempts allowed
- Track best score and improvement
- Question randomization
"""

import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from app.services.ai_service import ai_service
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


class QuizService:
    """Service for generating and managing quizzes"""

    # Quiz durations in minutes by question count
    QUIZ_DURATIONS = {
        5: 10,   # 5 questions = 10 minutes
        10: 20,  # 10 questions = 20 minutes
        15: 30,  # 15 questions = 30 minutes
        20: 40,  # 20 questions = 40 minutes
    }

    def generate_quiz(
        self,
        topic_id: str,
        topic_name: str,
        subject: str,
        grade: int,
        num_questions: int = 10,
        difficulty: str = "medium",
    ) -> Dict[str, Any]:
        """
        Generate a timed quiz with AI-generated questions

        Args:
            topic_id: Topic UUID
            topic_name: Name of the topic
            subject: Subject name
            grade: Grade level
            num_questions: Number of questions (5, 10, 15, 20)
            difficulty: Difficulty level (easy, medium, hard)

        Returns:
            Dictionary with quiz data
        """
        # Get quiz duration based on question count
        duration_minutes = self.QUIZ_DURATIONS.get(num_questions, 20)

        # Generate questions using AI (100% AI for variety)
        questions = self._generate_quiz_questions(
            topic_name, subject, grade, num_questions, difficulty
        )

        # Randomize question order
        random.shuffle(questions)

        # Add question numbers
        for i, q in enumerate(questions, 1):
            q["question_number"] = i

        quiz = {
            "topic_id": topic_id,
            "topic_name": topic_name,
            "subject": subject,
            "grade": grade,
            "difficulty": difficulty,
            "total_questions": len(questions),
            "questions": questions,
            "duration_minutes": duration_minutes,
            "max_score": len(questions),  # 1 point per question for quizzes
            "generated_at": datetime.utcnow().isoformat(),
        }

        return quiz

    def _generate_quiz_questions(
        self,
        topic_name: str,
        subject: str,
        grade: int,
        count: int,
        difficulty: str,
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions using Claude AI

        For quizzes, we use 100% AI generation to ensure:
        - Fresh questions each time
        - Variety across attempts
        - No predictability
        """
        try:
            # Get RAG context for the topic
            context = rag_service.get_context_for_topic(
                topic_name, grade=grade, subject=subject, n_results=3
            )

            # Use AI service to generate questions
            # For quizzes, prefer MCQ and True/False (faster to grade, objective)
            questions = ai_service.generate_questions(
                topic=topic_name,
                grade=grade,
                subject=subject,
                question_count=count,
                difficulty=difficulty,
                context=context,
                # Prefer objective question types for quizzes
                question_types=["MCQ", "True/False"],
            )

            # Ensure all questions have 1 point (quizzes are uniform scoring)
            for q in questions:
                q["points"] = 1

            return questions

        except Exception as e:
            logger.error(f"Error generating quiz questions: {e}")
            # Return fallback questions if AI fails
            return self._generate_fallback_questions(count)

    def _generate_fallback_questions(self, count: int) -> List[Dict[str, Any]]:
        """Generate simple fallback questions if AI fails"""
        questions = []
        for i in range(count):
            questions.append(
                {
                    "type": "MCQ",
                    "question": f"Sample question {i + 1}",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "Option A",
                    "points": 1,
                }
            )
        return questions

    def grade_quiz(
        self,
        questions: List[Dict[str, Any]],
        student_answers: Dict[str, str],
        time_taken_seconds: int,
        duration_minutes: int,
    ) -> Dict[str, Any]:
        """
        Grade a quiz submission

        Args:
            questions: List of questions from quiz
            student_answers: Dict mapping question_number to answer
            time_taken_seconds: Actual time taken by student
            duration_minutes: Allowed duration

        Returns:
            Grading result with score, feedback, and time analysis
        """
        total_score = 0
        max_score = len(questions)
        graded_answers = []

        # Check if time limit was exceeded
        time_limit_seconds = duration_minutes * 60
        time_exceeded = time_taken_seconds > time_limit_seconds

        for question in questions:
            q_num = question["question_number"]
            student_answer = student_answers.get(str(q_num), "").strip()

            if not student_answer:
                # No answer provided
                graded_answers.append(
                    {
                        "question_number": q_num,
                        "question": question["question"],
                        "student_answer": "",
                        "correct_answer": question.get("correct_answer", ""),
                        "score": 0,
                        "is_correct": False,
                        "feedback": "No answer provided",
                    }
                )
                continue

            # Grade based on question type
            is_correct = False
            feedback = ""

            if question["type"] in ["MCQ", "True/False"]:
                # Deterministic grading for objective questions
                correct_answer = question.get("correct_answer", "").strip()
                is_correct = student_answer.lower() == correct_answer.lower()
                score = 1 if is_correct else 0
                feedback = "Correct!" if is_correct else "Incorrect"
            else:
                # For any subjective questions (rare in quizzes), use simple matching
                correct_answer = question.get("correct_answer", "").strip()
                is_correct = student_answer.lower() == correct_answer.lower()
                score = 1 if is_correct else 0
                feedback = "Correct!" if is_correct else "Incorrect"

            graded_answers.append(
                {
                    "question_number": q_num,
                    "question": question["question"],
                    "student_answer": student_answer,
                    "correct_answer": question.get("correct_answer", ""),
                    "score": score,
                    "is_correct": is_correct,
                    "feedback": feedback,
                }
            )

            total_score += score

        percentage = (total_score / max_score * 100) if max_score > 0 else 0

        # Calculate time metrics
        avg_time_per_question = time_taken_seconds / max_score if max_score > 0 else 0

        return {
            "total_score": total_score,
            "max_score": max_score,
            "percentage": round(percentage, 2),
            "graded_answers": graded_answers,
            "passed": percentage >= 70,  # 70% passing for quizzes (higher than worksheets)
            "time_taken_seconds": time_taken_seconds,
            "time_limit_seconds": time_limit_seconds,
            "time_exceeded": time_exceeded,
            "avg_time_per_question": round(avg_time_per_question, 1),
        }

    def calculate_improvement(
        self,
        current_score: float,
        previous_scores: List[float],
    ) -> Dict[str, Any]:
        """
        Calculate improvement metrics across attempts

        Args:
            current_score: Current attempt score (percentage)
            previous_scores: List of previous attempt scores (percentages)

        Returns:
            Improvement analysis
        """
        if not previous_scores:
            return {
                "is_first_attempt": True,
                "improvement": 0,
                "best_score": current_score,
                "average_score": current_score,
                "total_attempts": 1,
            }

        all_scores = previous_scores + [current_score]
        best_score = max(all_scores)
        average_score = sum(all_scores) / len(all_scores)

        # Calculate improvement from last attempt
        improvement = current_score - previous_scores[-1] if previous_scores else 0

        return {
            "is_first_attempt": False,
            "improvement": round(improvement, 2),
            "best_score": round(best_score, 2),
            "average_score": round(average_score, 2),
            "total_attempts": len(all_scores),
            "is_best_score": current_score >= best_score,
        }


# Singleton instance
quiz_service = QuizService()
