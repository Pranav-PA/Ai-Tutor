"""Evaluation Agent - Scores answers and tracks performance."""
from typing import Dict, List, Any

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.services import llm_service


class EvaluationAgent(BaseAgent):
    """
    Evaluates quiz responses and tracks performance.
    
    Responsibilities:
    - Score MCQ answers (exact match)
    - Evaluate short answers using LLM
    - Evaluate conceptual answers with rubric
    - Identify weak areas from wrong answers
    - Track accuracy patterns
    """

    def __init__(self):
        super().__init__(
            name="evaluation_agent",
            description="Evaluates quiz answers and identifies weak areas"
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """Evaluate quiz submission."""
        questions = context.get("questions", [])
        user_answers = context.get("user_answers", {})  # {question_index: answer}
        topic_title = context.get("topic_title", "")

        if not questions or not user_answers:
            return AgentResult(success=False, error="No questions or answers to evaluate")

        results = []
        total_score = 0
        max_score = 0
        weak_areas = []

        for i, question in enumerate(questions):
            q_id = str(i)
            user_answer = user_answers.get(q_id, "")
            correct_answer = question.get("correct_answer", "")
            q_type = question.get("type", "mcq")
            points = question.get("points", 1)
            max_score += points

            # Evaluate based on question type
            if q_type == "mcq":
                evaluation = self._evaluate_mcq(user_answer, correct_answer)
            else:
                evaluation = await self._evaluate_open_answer(
                    question["question"], user_answer, correct_answer, q_type
                )

            score = points if evaluation["correct"] else (
                points * evaluation.get("partial_credit", 0)
            )
            total_score += score

            result_item = {
                "question_index": i,
                "question": question["question"],
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": evaluation["correct"],
                "score": score,
                "max_score": points,
                "feedback": evaluation.get("feedback", ""),
            }
            results.append(result_item)

            # Track weak areas
            if not evaluation["correct"]:
                weak_areas.append({
                    "question": question["question"],
                    "topic": topic_title,
                    "type": q_type,
                    "feedback": evaluation.get("feedback", ""),
                })

        percentage = (total_score / max_score * 100) if max_score > 0 else 0

        return AgentResult(
            success=True,
            data={
                "results": results,
                "total_score": total_score,
                "max_score": max_score,
                "percentage": round(percentage, 1),
                "weak_areas": weak_areas,
                "topic": topic_title,
            },
            next_agent="adaptive_agent"
        )

    def _evaluate_mcq(self, user_answer: str, correct_answer: str) -> Dict:
        """Evaluate MCQ answer (exact match)."""
        # Normalize answers for comparison
        user_clean = user_answer.strip().upper()[:1] if user_answer else ""
        correct_clean = correct_answer.strip().upper()[:1] if correct_answer else ""

        # Also check full text match
        is_correct = (
            user_clean == correct_clean or
            user_answer.strip().lower() == correct_answer.strip().lower()
        )

        return {
            "correct": is_correct,
            "feedback": "Correct!" if is_correct else f"Incorrect. The correct answer is: {correct_answer}",
        }

    async def _evaluate_open_answer(
        self,
        question: str,
        user_answer: str,
        correct_answer: str,
        q_type: str
    ) -> Dict:
        """Evaluate open-ended answer using LLM."""
        if not user_answer.strip():
            return {"correct": False, "partial_credit": 0, "feedback": "No answer provided."}

        system_prompt = """You are an expert evaluator. Assess the student's answer against 
        the correct answer.
        
        Return a JSON object:
        {
            "correct": true/false,
            "partial_credit": 0.0 to 1.0,
            "feedback": "Specific feedback about what's right/wrong"
        }
        
        Rules:
        - Award partial credit for partially correct answers
        - Consider semantic correctness, not just exact wording
        - Be fair but maintain standards
        - Provide constructive feedback"""

        prompt = f"""Question: {question}
        
Correct Answer: {correct_answer}

Student's Answer: {user_answer}

Evaluate the student's answer:"""

        result = await llm_service.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )

        return {
            "correct": result.get("correct", False),
            "partial_credit": result.get("partial_credit", 0),
            "feedback": result.get("feedback", ""),
        }
