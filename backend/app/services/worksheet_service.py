"""
Worksheet Generation Service - Hybrid Template + AI Approach

70% Template-based: Consistent quality, faster generation
30% AI-generated: Variety and creativity

Supports: MCQ, Short Answer, Numerical, True/False questions
"""

import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.services.ai_service import ai_service
from app.services.rag_service import rag_service

logger = logging.getLogger(__name__)


class WorksheetService:
    """Service for generating and managing worksheets"""

    # Question templates for different subjects and topics
    TEMPLATES = {
        "Mathematics": {
            "Fractions": [
                {
                    "type": "MCQ",
                    "question": "What is {num1}/{denom1} + {num2}/{denom2}?",
                    "generator": "fraction_addition",
                    "difficulty": "medium",
                },
                {
                    "type": "Short Answer",
                    "question": "Convert {improper} into a mixed number.",
                    "generator": "improper_to_mixed",
                    "difficulty": "easy",
                },
                {
                    "type": "True/False",
                    "question": "{num1}/{denom1} is equivalent to {num2}/{denom2}.",
                    "generator": "equivalent_fractions",
                    "difficulty": "easy",
                },
            ],
            "Algebra": [
                {
                    "type": "MCQ",
                    "question": "Solve for x: {coef}x + {const1} = {const2}",
                    "generator": "linear_equation",
                    "difficulty": "medium",
                },
                {
                    "type": "Short Answer",
                    "question": "Simplify: {expr}",
                    "generator": "simplify_expression",
                    "difficulty": "medium",
                },
            ],
        },
        "Science": {
            "Photosynthesis": [
                {
                    "type": "MCQ",
                    "question": "Which pigment is responsible for photosynthesis?",
                    "options": ["Chlorophyll", "Melanin", "Hemoglobin", "Carotene"],
                    "correct": "Chlorophyll",
                    "difficulty": "easy",
                },
                {
                    "type": "Short Answer",
                    "question": "Explain the role of sunlight in photosynthesis.",
                    "difficulty": "medium",
                },
            ],
        },
    }

    def generate_worksheet(
        self,
        topic_id: str,
        topic_name: str,
        subject: str,
        grade: int,
        num_questions: int = 10,
        difficulty: str = "medium",
    ) -> Dict[str, Any]:
        """
        Generate a worksheet with mix of template and AI questions

        Args:
            topic_id: Topic UUID
            topic_name: Name of the topic
            subject: Subject name
            grade: Grade level
            num_questions: Total questions to generate
            difficulty: Difficulty level (easy, medium, hard)

        Returns:
            Dictionary with worksheet data
        """
        # Calculate split: 70% template, 30% AI
        template_count = int(num_questions * 0.7)
        ai_count = num_questions - template_count

        questions = []

        # Generate template-based questions
        template_questions = self._generate_template_questions(
            topic_name, subject, grade, template_count, difficulty
        )
        questions.extend(template_questions)

        # Generate AI questions
        ai_questions = self._generate_ai_questions(
            topic_name, subject, grade, ai_count, difficulty
        )
        questions.extend(ai_questions)

        # Shuffle to mix template and AI questions
        random.shuffle(questions)

        # Add question numbers
        for i, q in enumerate(questions, 1):
            q["question_number"] = i

        worksheet = {
            "topic_id": topic_id,
            "topic_name": topic_name,
            "subject": subject,
            "grade": grade,
            "difficulty": difficulty,
            "total_questions": len(questions),
            "questions": questions,
            "max_score": len(questions),
            "generated_at": datetime.utcnow().isoformat(),
        }

        return worksheet

    def _generate_template_questions(
        self,
        topic_name: str,
        subject: str,
        grade: int,
        count: int,
        difficulty: str,
    ) -> List[Dict[str, Any]]:
        """Generate questions from templates"""
        questions = []

        # Get templates for this subject/topic
        templates = self.TEMPLATES.get(subject, {}).get(topic_name, [])

        if not templates:
            # No templates available, return empty list
            logger.warning(
                f"No templates found for {subject} - {topic_name}, will use AI generation"
            )
            return questions

        # Filter by difficulty if possible
        difficulty_templates = [
            t for t in templates if t.get("difficulty") == difficulty
        ]
        if not difficulty_templates:
            difficulty_templates = templates

        # Generate questions from templates
        for _ in range(min(count, len(difficulty_templates) * 3)):
            template = random.choice(difficulty_templates)
            question = self._instantiate_template(template, grade)
            if question:
                questions.append(question)

        return questions[:count]

    def _instantiate_template(
        self, template: Dict[str, Any], grade: int
    ) -> Optional[Dict[str, Any]]:
        """Instantiate a template with random values"""
        try:
            question_type = template["type"]

            if question_type == "MCQ" and "options" in template:
                # Static MCQ with predefined options
                return {
                    "type": "MCQ",
                    "question": template["question"],
                    "options": template["options"],
                    "correct_answer": template["correct"],
                    "points": 1,
                }

            elif question_type == "MCQ" and "generator" in template:
                # Dynamic MCQ with generator
                return self._generate_from_template(template, grade)

            elif question_type == "Short Answer":
                return {
                    "type": "Short Answer",
                    "question": template["question"],
                    "points": 2,
                }

            elif question_type == "True/False":
                # Generate true/false question
                return self._generate_true_false(template, grade)

            else:
                return None

        except Exception as e:
            logger.error(f"Error instantiating template: {e}")
            return None

    def _generate_from_template(
        self, template: Dict[str, Any], grade: int
    ) -> Dict[str, Any]:
        """Generate question from template with generator"""
        generator = template.get("generator")

        if generator == "fraction_addition":
            # Generate fraction addition problem
            num1, denom1 = random.randint(1, 10), random.randint(2, 12)
            num2, denom2 = random.randint(1, 10), random.randint(2, 12)

            # Calculate correct answer
            from fractions import Fraction

            result = Fraction(num1, denom1) + Fraction(num2, denom2)

            question_text = template["question"].format(
                num1=num1, denom1=denom1, num2=num2, denom2=denom2
            )

            # Generate options
            options = [str(result)]
            while len(options) < 4:
                wrong = Fraction(
                    random.randint(1, 20), random.randint(2, 12)
                )
                if str(wrong) not in options:
                    options.append(str(wrong))

            random.shuffle(options)

            return {
                "type": "MCQ",
                "question": question_text,
                "options": options,
                "correct_answer": str(result),
                "points": 1,
            }

        elif generator == "linear_equation":
            # Generate linear equation
            coef = random.randint(2, 10)
            const1 = random.randint(1, 20)
            const2 = random.randint(20, 50)

            x_value = (const2 - const1) / coef

            question_text = template["question"].format(
                coef=coef, const1=const1, const2=const2
            )

            # Generate options
            options = [str(int(x_value)) if x_value.is_integer() else f"{x_value:.1f}"]
            while len(options) < 4:
                wrong = random.randint(1, 20)
                if str(wrong) not in options:
                    options.append(str(wrong))

            random.shuffle(options)

            return {
                "type": "MCQ",
                "question": question_text,
                "options": options,
                "correct_answer": options[0],
                "points": 1,
            }

        # Default fallback
        return {
            "type": "Short Answer",
            "question": template.get("question", "Answer the question."),
            "points": 2,
        }

    def _generate_true_false(
        self, template: Dict[str, Any], grade: int
    ) -> Dict[str, Any]:
        """Generate true/false question"""
        # For equivalent fractions
        if template.get("generator") == "equivalent_fractions":
            num1, denom1 = random.randint(1, 10), random.randint(2, 12)

            # 50% chance of true statement
            is_true = random.choice([True, False])

            if is_true:
                # Multiply both by same factor
                factor = random.randint(2, 5)
                num2, denom2 = num1 * factor, denom1 * factor
            else:
                # Random different fraction
                num2, denom2 = random.randint(1, 10), random.randint(2, 12)

            question_text = template["question"].format(
                num1=num1, denom1=denom1, num2=num2, denom2=denom2
            )

            return {
                "type": "True/False",
                "question": question_text,
                "correct_answer": "True" if is_true else "False",
                "points": 1,
            }

        # Default true/false
        return {
            "type": "True/False",
            "question": template.get("question", "True or False?"),
            "correct_answer": random.choice(["True", "False"]),
            "points": 1,
        }

    def _generate_ai_questions(
        self,
        topic_name: str,
        subject: str,
        grade: int,
        count: int,
        difficulty: str,
    ) -> List[Dict[str, Any]]:
        """Generate questions using Claude AI"""
        if count == 0:
            return []

        try:
            # Get RAG context for the topic
            context = rag_service.get_context_for_topic(
                topic_name, grade=grade, subject=subject, n_results=3
            )

            # Use AI service to generate questions
            questions = ai_service.generate_questions(
                topic=topic_name,
                grade=grade,
                subject=subject,
                question_count=count,
                difficulty=difficulty,
                context=context,
            )

            # Ensure all questions have required fields
            for q in questions:
                if "points" not in q:
                    q["points"] = 2 if q["type"] == "Short Answer" else 1

            return questions

        except Exception as e:
            logger.error(f"Error generating AI questions: {e}")
            return []

    def grade_worksheet(
        self,
        questions: List[Dict[str, Any]],
        student_answers: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Grade a worksheet submission

        Args:
            questions: List of questions from worksheet
            student_answers: Dict mapping question_number to answer

        Returns:
            Grading result with score and feedback
        """
        from app.services.education_service import education_service

        total_score = 0
        max_score = sum(q.get("points", 1) for q in questions)
        graded_answers = []

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
                        "max_score": question.get("points", 1),
                        "feedback": "No answer provided",
                    }
                )
                continue

            # Grade using education service (multi-tier grading)
            grading_result = education_service.grade_student_answer(
                question=question["question"],
                question_type=question["type"],
                correct_answer=question.get("correct_answer", ""),
                student_answer=student_answer,
                max_points=question.get("points", 1),
            )

            graded_answers.append(
                {
                    "question_number": q_num,
                    "question": question["question"],
                    "student_answer": student_answer,
                    "correct_answer": question.get("correct_answer", ""),
                    "score": grading_result["score"],
                    "max_score": question.get("points", 1),
                    "feedback": grading_result.get("feedback", ""),
                    "is_correct": grading_result.get("is_correct", False),
                }
            )

            total_score += grading_result["score"]

        percentage = (total_score / max_score * 100) if max_score > 0 else 0

        return {
            "total_score": round(total_score, 2),
            "max_score": max_score,
            "percentage": round(percentage, 2),
            "graded_answers": graded_answers,
            "passed": percentage >= 60,  # 60% passing grade
        }


# Singleton instance
worksheet_service = WorksheetService()
