"""
Integrated education service combining AI, RAG, and caching
"""

from typing import List, Dict, Any, Optional
import logging

from app.services.ai_service import claude_service
from app.services.rag_service import rag_service
from app.services.cache_service import cache_service

logger = logging.getLogger(__name__)


class EducationService:
    """Integrated service for educational AI features"""

    def __init__(self):
        """Initialize education service"""
        self.ai_service = claude_service
        self.rag_service = rag_service
        self.cache_service = cache_service

    def explain_topic(
        self,
        topic_name: str,
        grade: int,
        subject: Optional[str] = None,
        difficulty: str = "medium",
        use_cache: bool = True
    ) -> str:
        """
        Generate explanation for a topic with RAG context

        Args:
            topic_name: Topic to explain
            grade: Student grade
            subject: Subject name
            difficulty: Difficulty level
            use_cache: Whether to use caching

        Returns:
            Explanation text
        """
        # Check cache first
        if use_cache:
            cache_key_data = {
                "topic": topic_name,
                "grade": grade,
                "subject": subject,
                "difficulty": difficulty
            }
            cached_result = self.cache_service.get("explanation", cache_key_data)
            if cached_result:
                logger.info(f"Cache hit for explanation: {topic_name}")
                return cached_result

        # Get context from RAG
        logger.info(f"Retrieving context for topic: {topic_name}")
        context = self.rag_service.get_context_for_topic(
            topic=topic_name,
            grade=grade,
            subject=subject,
            max_chunks=5
        )

        # Generate explanation with AI
        logger.info(f"Generating explanation for topic: {topic_name}")
        explanation = self.ai_service.explain_concept(
            topic=topic_name,
            grade=grade,
            context=context if context else None,
            difficulty=difficulty
        )

        # Cache the result
        if use_cache:
            self.cache_service.set(
                "explanation",
                cache_key_data,
                explanation,
                ttl=7200  # 2 hours
            )

        return explanation

    def generate_worksheet_questions(
        self,
        topic_name: str,
        grade: int,
        question_count: int = 5,
        question_types: Optional[List[str]] = None,
        difficulty: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Generate questions for a worksheet

        Args:
            topic_name: Topic name
            grade: Student grade
            question_count: Number of questions
            question_types: Types of questions
            difficulty: Difficulty level

        Returns:
            List of questions
        """
        # Generate questions with AI
        logger.info(f"Generating {question_count} questions for topic: {topic_name}")
        questions = self.ai_service.generate_questions(
            topic=topic_name,
            grade=grade,
            question_count=question_count,
            question_types=question_types,
            difficulty=difficulty
        )

        return questions

    def grade_student_answer(
        self,
        question: str,
        correct_answer: str,
        student_answer: str,
        question_type: str = "short_answer",
        max_points: int = 5
    ) -> Dict[str, Any]:
        """
        Grade a student answer

        Args:
            question: Question text
            correct_answer: Correct answer
            student_answer: Student's answer
            question_type: Type of question
            max_points: Maximum points

        Returns:
            Grading result
        """
        # For MCQ and True/False, use deterministic grading
        if question_type in ["mcq", "true_false"]:
            is_correct = student_answer.strip().lower() == correct_answer.strip().lower()
            return {
                "score": max_points if is_correct else 0,
                "is_correct": is_correct,
                "feedback": "Correct!" if is_correct else f"Incorrect. The correct answer is: {correct_answer}",
                "mistakes": [] if is_correct else ["Incorrect answer"]
            }

        # For numerical, use pattern-based grading with tolerance
        if question_type == "numerical":
            try:
                student_num = float(student_answer.strip())
                correct_num = float(correct_answer.strip())
                tolerance = 0.01  # 1% tolerance

                is_correct = abs(student_num - correct_num) <= tolerance * abs(correct_num)

                return {
                    "score": max_points if is_correct else 0,
                    "is_correct": is_correct,
                    "feedback": "Correct!" if is_correct else f"Incorrect. The correct answer is: {correct_answer}",
                    "mistakes": [] if is_correct else ["Incorrect numerical answer"]
                }
            except ValueError:
                return {
                    "score": 0,
                    "is_correct": False,
                    "feedback": "Invalid numerical answer. Please provide a number.",
                    "mistakes": ["Invalid format"]
                }

        # For short answers, use AI grading
        logger.info(f"AI grading for question: {question[:50]}...")
        result = self.ai_service.grade_answer(
            question=question,
            correct_answer=correct_answer,
            student_answer=student_answer,
            question_type=question_type,
            max_points=max_points
        )

        return result

    def get_chat_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        grade: int,
        topic: Optional[str] = None,
        use_rag: bool = True
    ) -> tuple[str, List[str]]:
        """
        Get chatbot response for doubt clearing

        Args:
            user_message: User's question
            conversation_history: Previous messages
            grade: Student grade
            topic: Optional topic for context
            use_rag: Whether to use RAG for context

        Returns:
            Tuple of (response_text, sources)
        """
        context = None
        sources = []

        # Get context from RAG if enabled
        if use_rag and topic:
            logger.info(f"Retrieving context for chat about: {topic}")
            results = self.rag_service.search(
                query=user_message,
                n_results=3,
                grade=grade
            )

            if results:
                # Combine context
                context_parts = []
                for result in results:
                    context_parts.append(result['content'])
                    # Track sources
                    metadata = result.get('metadata', {})
                    if metadata.get('chapter'):
                        source = f"{metadata.get('subject', 'NCERT')} - {metadata['chapter']}"
                        if metadata.get('page'):
                            source += f" (Page {metadata['page']})"
                        sources.append(source)

                context = "\n\n".join(context_parts)

        # Generate response
        logger.info("Generating chat response with AI")
        response = self.ai_service.chat_response(
            user_message=user_message,
            conversation_history=conversation_history,
            context=context,
            grade=grade
        )

        return response, sources

    def get_rag_stats(self) -> Dict[str, Any]:
        """
        Get RAG system statistics

        Returns:
            Statistics dictionary
        """
        return self.rag_service.get_collection_stats()

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics

        Returns:
            Statistics dictionary
        """
        return self.cache_service.get_stats()


# Global instance
education_service = EducationService()
