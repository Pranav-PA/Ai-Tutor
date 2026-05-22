"""Quiz Agent - Generates quizzes (MCQ, Short Answer, Conceptual)."""
from typing import Dict, List, Any

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.services import llm_service, vector_store


class QuizAgent(BaseAgent):
    """
    Generates quizzes for assessment.
    
    Responsibilities:
    - Generate MCQs with distractors
    - Generate short answer questions
    - Generate conceptual/application questions
    - Adjust difficulty based on learner level
    - Use source material for question generation
    """

    def __init__(self):
        super().__init__(
            name="quiz_agent",
            description="Generates assessment quizzes from course material"
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """Generate a quiz for the given topic."""
        course_id = context.course_id
        topic_title = context.get("topic_title", "")
        num_questions = context.get("num_questions", 5)
        difficulty = context.get("difficulty", "intermediate")
        question_types = context.get("question_types", ["mcq", "short_answer"])

        if not topic_title:
            return AgentResult(success=False, error="No topic specified")

        # Retrieve relevant content
        relevant_content = await vector_store.search(
            course_id=course_id,
            query=topic_title,
            top_k=8
        )

        source_content = "\n\n".join([text for text, score, meta in relevant_content if score > 0.3])

        # Generate questions
        questions = await self._generate_questions(
            topic_title, source_content, num_questions, difficulty, question_types
        )

        return AgentResult(
            success=True,
            data={
                "questions": questions,
                "topic": topic_title,
                "difficulty": difficulty,
            }
        )

    async def _generate_questions(
        self,
        topic: str,
        source: str,
        num_questions: int,
        difficulty: str,
        question_types: List[str]
    ) -> List[Dict]:
        """Generate quiz questions using LLM."""
        type_instructions = {
            "mcq": "Multiple choice with 4 options (A, B, C, D). Include realistic distractors.",
            "short_answer": "Questions requiring 1-3 sentence answers.",
            "conceptual": "Questions testing deep understanding, application, or analysis."
        }

        types_str = "\n".join([
            f"- {qt}: {type_instructions.get(qt, '')}"
            for qt in question_types
        ])

        system_prompt = """You are an expert question paper designer. Generate high-quality 
        assessment questions based on the provided material.
        
        Return a JSON object:
        {
            "questions": [
                {
                    "type": "mcq|short_answer|conceptual",
                    "question": "Question text",
                    "options": ["A) ...", "B) ...", "C) ...", "D) ..."],  // only for MCQ
                    "correct_answer": "The correct answer",
                    "explanation": "Why this is correct",
                    "difficulty": "beginner|intermediate|advanced",
                    "points": 1
                }
            ]
        }
        
        IMPORTANT:
        - Questions must be answerable from the source material
        - MCQ distractors should be plausible but clearly wrong
        - Vary question complexity
        - Include explanations for each answer"""

        prompt = f"""Generate {num_questions} questions about "{topic}"

Difficulty: {difficulty}
Question Types Required:
{types_str}

Source Material:
{source[:5000]}

Generate diverse, high-quality questions:"""

        result = await llm_service.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.6,
            max_tokens=4000
        )

        questions = result.get("questions", [])

        # Validate and clean questions
        cleaned_questions = []
        for i, q in enumerate(questions):
            cleaned_q = {
                "type": q.get("type", "mcq"),
                "question": q.get("question", ""),
                "correct_answer": q.get("correct_answer", ""),
                "explanation": q.get("explanation", ""),
                "difficulty": q.get("difficulty", difficulty),
                "points": q.get("points", 1),
                "order": i + 1,
            }
            if q.get("type") == "mcq":
                cleaned_q["options"] = q.get("options", [])
            cleaned_questions.append(cleaned_q)

        return cleaned_questions
