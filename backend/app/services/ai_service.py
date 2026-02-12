"""
Claude AI service for generating educational content
"""

import anthropic
from typing import Optional, List, Dict, Any
import logging
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class ClaudeService:
    """Claude AI service wrapper"""

    def __init__(self):
        """Initialize Claude client"""
        if not settings.ANTHROPIC_API_KEY:
            logger.warning("ANTHROPIC_API_KEY not set. AI features will not work.")
            self.client = None
        else:
            self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        self.model = "claude-3-5-sonnet-20241022"  # Latest Claude model

    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate completion using Claude

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)

        Returns:
            Generated text
        """
        if not self.client:
            raise ValueError("Claude API key not configured")

        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages,
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)

            # Extract text from response
            return response.content[0].text

        except Exception as e:
            logger.error(f"Error generating completion: {str(e)}")
            raise

    def explain_concept(
        self,
        topic: str,
        grade: int,
        context: Optional[str] = None,
        difficulty: str = "medium"
    ) -> str:
        """
        Generate explanation for a concept

        Args:
            topic: Topic name
            grade: Student grade (3-10)
            context: Optional NCERT context from RAG
            difficulty: Difficulty level (easy, medium, hard)

        Returns:
            Concept explanation
        """
        system_prompt = f"""You are an expert Indian education tutor specializing in NCERT curriculum for grades 3-10.
Your task is to explain concepts clearly and accurately for Grade {grade} students.

Guidelines:
- Use simple, age-appropriate language
- Include relevant examples from Indian context
- Break down complex concepts into simple parts
- Use analogies and real-world examples
- Reference NCERT textbooks when relevant
- Format explanations with markdown (headings, lists, bold)
- Include practice tips where applicable"""

        prompt_parts = [
            f"Topic: {topic}",
            f"Grade: {grade}",
            f"Difficulty: {difficulty}",
        ]

        if context:
            prompt_parts.append(f"\nNCERT Context:\n{context}")

        prompt_parts.append(f"\nProvide a clear, comprehensive explanation of '{topic}' suitable for Grade {grade} students following the NCERT curriculum.")

        prompt = "\n\n".join(prompt_parts)

        return self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=2048,
            temperature=0.7
        )

    def generate_questions(
        self,
        topic: str,
        grade: int,
        question_count: int = 5,
        question_types: Optional[List[str]] = None,
        difficulty: str = "medium"
    ) -> List[Dict[str, Any]]:
        """
        Generate questions for a topic

        Args:
            topic: Topic name
            grade: Student grade
            question_count: Number of questions
            question_types: Types of questions (mcq, short_answer, numerical, true_false)
            difficulty: Difficulty level

        Returns:
            List of question objects
        """
        if question_types is None:
            question_types = ["mcq", "short_answer", "numerical"]

        system_prompt = f"""You are an expert question generator for NCERT curriculum (Grade {grade}).
Generate high-quality, curriculum-aligned questions.

Output Format: JSON array of questions
Each question must have:
- id: unique identifier (string)
- question_text: the question (string)
- question_type: type (mcq, short_answer, numerical, true_false)
- options: array of options (for mcq only, 4 options)
- correct_answer: the correct answer (string)
- explanation: brief explanation of answer (string)
- points: point value (1-5, integer)

Important:
- Questions must be grade-appropriate
- Follow NCERT curriculum standards
- Provide clear, unambiguous questions
- Include varied difficulty within the set"""

        prompt = f"""Generate {question_count} questions on the topic: "{topic}"

Grade: {grade}
Question Types: {', '.join(question_types)}
Difficulty: {difficulty}

Return ONLY a valid JSON array of questions, no additional text."""

        response = self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=3000,
            temperature=0.8
        )

        try:
            # Extract JSON from response
            # Sometimes Claude wraps JSON in markdown code blocks
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif json_str.startswith("```"):
                json_str = json_str.split("```")[1].split("```")[0].strip()

            questions = json.loads(json_str)
            return questions

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse questions JSON: {str(e)}\nResponse: {response}")
            raise ValueError("Failed to generate valid questions")

    def grade_answer(
        self,
        question: str,
        correct_answer: str,
        student_answer: str,
        question_type: str = "short_answer",
        max_points: int = 5
    ) -> Dict[str, Any]:
        """
        Grade a student's answer using AI

        Args:
            question: The question text
            correct_answer: The correct answer
            student_answer: Student's answer
            question_type: Type of question
            max_points: Maximum points for this question

        Returns:
            Grading result with score and feedback
        """
        system_prompt = """You are an expert grader for NCERT curriculum assessments.
Grade student answers fairly and provide constructive feedback.

Output Format: JSON object with:
- score: points earned (number, 0 to max_points)
- is_correct: whether answer is correct (boolean)
- feedback: constructive feedback (string)
- mistakes: list of mistakes if any (array of strings)

Grading Guidelines:
- For short answers, accept equivalent correct answers
- Award partial credit for partially correct answers
- Be lenient with minor spelling/grammar errors
- Focus on conceptual understanding
- Provide encouraging, constructive feedback"""

        prompt = f"""Grade this answer:

Question: {question}
Question Type: {question_type}
Correct Answer: {correct_answer}
Student Answer: {student_answer}
Maximum Points: {max_points}

Return ONLY a valid JSON object with the grading result."""

        response = self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=500,
            temperature=0.3  # Lower temperature for consistent grading
        )

        try:
            # Extract JSON from response
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str.split("```json")[1].split("```")[0].strip()
            elif json_str.startswith("```"):
                json_str = json_str.split("```")[1].split("```")[0].strip()

            result = json.loads(json_str)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse grading JSON: {str(e)}\nResponse: {response}")
            # Return default failing grade
            return {
                "score": 0,
                "is_correct": False,
                "feedback": "Unable to grade answer automatically.",
                "mistakes": []
            }

    def chat_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[str] = None,
        grade: int = 5
    ) -> str:
        """
        Generate chat response for doubt clearing

        Args:
            user_message: User's question
            conversation_history: Previous messages [{"role": "user/assistant", "content": "..."}]
            context: Optional NCERT context from RAG
            grade: Student grade

        Returns:
            AI response
        """
        system_prompt = f"""You are an expert AI tutor for NCERT curriculum (Grade {grade}).
Help students clear their doubts with patience and clarity.

Guidelines:
- Be friendly, encouraging, and patient
- Explain concepts step-by-step
- Use simple, age-appropriate language
- Provide examples to illustrate concepts
- Reference NCERT textbooks when relevant
- Ask follow-up questions to check understanding
- If context is provided, use it to give accurate answers
- Always cite sources when referencing textbook content"""

        # Build conversation
        messages = []

        # Add conversation history
        for msg in conversation_history[-10:]:  # Last 10 messages
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # Add current message with context
        user_content = user_message
        if context:
            user_content = f"Context from NCERT:\n{context}\n\nQuestion: {user_message}"

        messages.append({
            "role": "user",
            "content": user_content
        })

        # Generate response
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                temperature=0.7,
                system=system_prompt,
                messages=messages
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error generating chat response: {str(e)}")
            raise


# Global instance
claude_service = ClaudeService()
ai_service = claude_service
