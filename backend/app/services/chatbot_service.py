"""
Chatbot Service - AI-powered doubt clearing with RAG

Features:
- Context-aware responses using conversation history
- RAG integration for NCERT content
- Source attribution with page numbers
- Grade-appropriate language
- Patient, encouraging tone
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.services.ai_service import ai_service
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


class ChatbotService:
    """Service for managing AI chatbot conversations"""

    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        student_grade: int,
        topic: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generate AI response to student's doubt

        Args:
            user_message: Student's question
            conversation_history: Previous messages in conversation
            student_grade: Student's grade level
            topic: Optional topic context
            subject: Optional subject context

        Returns:
            Dictionary with response and sources
        """
        try:
            # Get RAG context if topic/subject provided
            context = None
            sources = []

            if topic or subject:
                # Extract context from NCERT
                search_query = topic or subject or user_message
                rag_results = rag_service.search(
                    query=search_query,
                    n_results=3,
                    grade=student_grade,
                    subject=subject,
                )

                if rag_results:
                    # Format context
                    context_parts = []
                    for result in rag_results:
                        context_parts.append(result["text"])
                        sources.append(
                            {
                                "text": result["text"][:200] + "...",
                                "metadata": result["metadata"],
                            }
                        )

                    context = "\n\n".join(context_parts)

            # Generate response using AI service
            response = ai_service.chat_response(
                user_message=user_message,
                conversation_history=conversation_history,
                grade=student_grade,
                subject=subject,
                context=context,
            )

            return {
                "response": response,
                "sources": sources,
                "has_context": context is not None,
            }

        except Exception as e:
            logger.error(f"Error generating chatbot response: {e}")
            return {
                "response": "I apologize, but I'm having trouble answering right now. Could you please rephrase your question?",
                "sources": [],
                "has_context": False,
            }

    def suggest_related_topics(
        self,
        current_topic: str,
        subject: str,
        grade: int,
    ) -> List[str]:
        """
        Suggest related topics based on current conversation

        Args:
            current_topic: Current topic being discussed
            subject: Subject area
            grade: Student's grade

        Returns:
            List of related topic suggestions
        """
        try:
            # Use RAG to find related content
            results = rag_service.search(
                query=current_topic,
                n_results=5,
                grade=grade,
                subject=subject,
            )

            # Extract unique topics from metadata
            topics = set()
            for result in results:
                metadata = result.get("metadata", {})
                if "chapter" in metadata:
                    topics.add(metadata["chapter"])

            return list(topics)[:3]  # Return top 3

        except Exception as e:
            logger.error(f"Error suggesting topics: {e}")
            return []

    def detect_topic(
        self,
        message: str,
        grade: int,
        subject: Optional[str] = None,
    ) -> Optional[str]:
        """
        Detect the topic being discussed from message

        Args:
            message: Student's message
            grade: Student's grade
            subject: Optional subject filter

        Returns:
            Detected topic name or None
        """
        try:
            # Search for relevant content
            results = rag_service.search(
                query=message,
                n_results=1,
                grade=grade,
                subject=subject,
            )

            if results:
                metadata = results[0].get("metadata", {})
                return metadata.get("chapter") or metadata.get("topic")

            return None

        except Exception as e:
            logger.error(f"Error detecting topic: {e}")
            return None

    def generate_conversation_summary(
        self,
        messages: List[Dict[str, Any]],
    ) -> str:
        """
        Generate a summary of the conversation

        Args:
            messages: List of messages in conversation

        Returns:
            Summary text
        """
        try:
            # Take first and last few messages
            if len(messages) <= 5:
                relevant_messages = messages
            else:
                # First 2 and last 3
                relevant_messages = messages[:2] + messages[-3:]

            # Format for AI
            conversation_text = "\n".join(
                [
                    f"{'Student' if m['role'] == 'user' else 'Tutor'}: {m['content']}"
                    for m in relevant_messages
                ]
            )

            # Generate summary (simple version - could use AI)
            topics_discussed = set()
            for msg in messages:
                if msg.get("role") == "user":
                    # Extract potential topics (simplified)
                    words = msg["content"].split()
                    for word in words:
                        if len(word) > 5 and word[0].isupper():
                            topics_discussed.add(word)

            if topics_discussed:
                return f"Discussed: {', '.join(list(topics_discussed)[:3])}"
            else:
                return "General discussion about the topic"

        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Conversation summary"

    def validate_message(self, message: str) -> Dict[str, Any]:
        """
        Validate student's message

        Args:
            message: Student's message

        Returns:
            Validation result
        """
        message = message.strip()

        if not message:
            return {
                "valid": False,
                "error": "Message cannot be empty",
            }

        if len(message) < 3:
            return {
                "valid": False,
                "error": "Message is too short. Please provide more details.",
            }

        if len(message) > 2000:
            return {
                "valid": False,
                "error": "Message is too long. Please keep it under 2000 characters.",
            }

        # Check for inappropriate content (basic check)
        inappropriate_words = ["spam", "test123", "asdfgh"]
        lower_message = message.lower()
        if any(word in lower_message for word in inappropriate_words):
            return {
                "valid": False,
                "error": "Message contains inappropriate content.",
            }

        return {"valid": True}


# Singleton instance
chatbot_service = ChatbotService()
