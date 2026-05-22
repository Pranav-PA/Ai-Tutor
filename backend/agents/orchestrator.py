"""Multi-agent orchestration system."""
from typing import Dict, Any, List, Optional
from backend.agents.prompts import (
    SYLLABUS_ANALYZER_PROMPT, TEACHING_AGENT_PROMPT, QUIZ_AGENT_PROMPT,
    REVISION_AGENT_PROMPT, MEMORY_AGENT_PROMPT, QUESTION_PAPER_AGENT_PROMPT,
    FLASHCARD_AGENT_PROMPT, ANALYTICS_AGENT_PROMPT
)
from backend.services.ai_provider import chat_completion, json_completion, stream_chat_completion
from backend.rag.vector_store import vector_store
from backend.config import TEACHING_TEMPERATURE, QUIZ_TEMPERATURE


class AgentOrchestrator:
    """Orchestrates multiple AI agents for the tutoring system."""

    def __init__(self):
        pass

    def _get_context(self, course_id: int, query: str, n_results: int = 5) -> str:
        """Retrieve relevant context from vector store."""
        docs = vector_store.search(course_id, query, n_results=n_results)
        if docs:
            context_parts = []
            for i, doc in enumerate(docs):
                context_parts.append(f"[Source {i+1}]: {doc['text']}")
            return "\n\n".join(context_parts)
        return ""

    async def teach(
        self,
        course_id: int,
        query: str,
        mode: str = "detailed",
        learning_style: str = "balanced",
        chat_history: List[dict] = None
    ):
        """Teaching agent - explains concepts with RAG context."""
        # Get relevant context from uploaded notes
        context = self._get_context(course_id, query)

        messages = [
            {"role": "system", "content": TEACHING_AGENT_PROMPT},
        ]

        # Add context
        if context:
            messages.append({
                "role": "system",
                "content": f"STUDENT'S NOTES/MATERIALS (use these as primary source):\n{context}"
            })

        # Add learning preferences
        messages.append({
            "role": "system",
            "content": f"Student's learning style: {learning_style}\nTeaching mode: {mode}"
        })

        # Add chat history
        if chat_history:
            for msg in chat_history[-10:]:  # Last 10 messages
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": query})

        # Stream response
        async for chunk in stream_chat_completion(messages, temperature=TEACHING_TEMPERATURE):
            yield chunk

    def analyze_syllabus(self, course_id: int, content: str) -> Dict[str, Any]:
        """Analyze syllabus content and create learning roadmap."""
        messages = [
            {"role": "system", "content": SYLLABUS_ANALYZER_PROMPT},
            {"role": "user", "content": f"Analyze this syllabus/course content and create a structured learning roadmap:\n\n{content[:8000]}"}
        ]
        return json_completion(messages, temperature=0.3)

    def generate_quiz(
        self,
        course_id: int,
        topic: Optional[str] = None,
        quiz_type: str = "mcq",
        difficulty: str = "medium",
        num_questions: int = 5
    ) -> Dict[str, Any]:
        """Generate a quiz based on course content."""
        # Get context for the topic
        query = topic or "key concepts and important topics"
        context = self._get_context(course_id, query, n_results=8)

        messages = [
            {"role": "system", "content": QUIZ_AGENT_PROMPT},
        ]

        if context:
            messages.append({
                "role": "system",
                "content": f"COURSE MATERIALS (base questions on this content):\n{context}"
            })

        prompt = f"Generate a {difficulty} difficulty quiz with {num_questions} {quiz_type} questions"
        if topic:
            prompt += f" on the topic: {topic}"
        prompt += f"\nEnsure questions test understanding and application, not just recall."

        messages.append({"role": "user", "content": prompt})

        return json_completion(messages, temperature=QUIZ_TEMPERATURE)

    def generate_flashcards(
        self,
        course_id: int,
        topic: Optional[str] = None,
        num_cards: int = 10
    ) -> Dict[str, Any]:
        """Generate flashcards for spaced repetition."""
        query = topic or "key concepts definitions formulas"
        context = self._get_context(course_id, query, n_results=8)

        messages = [
            {"role": "system", "content": FLASHCARD_AGENT_PROMPT},
        ]

        if context:
            messages.append({
                "role": "system",
                "content": f"COURSE MATERIALS:\n{context}"
            })

        prompt = f"Generate {num_cards} flashcards"
        if topic:
            prompt += f" for the topic: {topic}"
        prompt += "\nFocus on key concepts, definitions, formulas, and important facts."

        messages.append({"role": "user", "content": prompt})

        return json_completion(messages, temperature=0.5)

    def generate_revision(
        self,
        course_id: int,
        revision_type: str = "cheat_sheet",
        topic: Optional[str] = None
    ) -> str:
        """Generate revision material."""
        query = topic or "complete syllabus overview all topics"
        context = self._get_context(course_id, query, n_results=10)

        messages = [
            {"role": "system", "content": REVISION_AGENT_PROMPT},
        ]

        if context:
            messages.append({
                "role": "system",
                "content": f"COURSE MATERIALS:\n{context}"
            })

        type_descriptions = {
            "cheat_sheet": "a concise cheat sheet with all key points, formulas, and definitions",
            "formula_sheet": "a comprehensive formula sheet organized by topic",
            "quick_notes": "quick revision notes highlighting the most important concepts",
            "exam_summary": "a 'night before exam' summary with the most critical information"
        }

        prompt = f"Create {type_descriptions.get(revision_type, 'revision notes')}"
        if topic:
            prompt += f" for the topic: {topic}"

        messages.append({"role": "user", "content": prompt})

        return chat_completion(messages, temperature=0.3)

    def generate_question_paper(
        self,
        course_id: int,
        total_marks: int = 100,
        duration_minutes: int = 180
    ) -> Dict[str, Any]:
        """Generate a model question paper."""
        context = self._get_context(course_id, "exam questions important topics all units", n_results=15)

        messages = [
            {"role": "system", "content": QUESTION_PAPER_AGENT_PROMPT},
        ]

        if context:
            messages.append({
                "role": "system",
                "content": f"COURSE MATERIALS:\n{context}"
            })

        prompt = f"""Generate a model question paper with:
- Total marks: {total_marks}
- Duration: {duration_minutes} minutes
- Include sections for short answers, long answers, and application questions
- Cover all units/topics evenly
- Include difficulty gradient"""

        messages.append({"role": "user", "content": prompt})

        return json_completion(messages, temperature=QUIZ_TEMPERATURE)

    def generate_study_plan(
        self,
        course_id: int,
        hours_per_day: float,
        days_until_exam: int,
        topics: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a personalized study plan."""
        context = self._get_context(course_id, "syllabus units topics", n_results=10)

        messages = [
            {"role": "system", "content": """You are a Study Planner Agent. Create optimal study schedules.
            
Output MUST be valid JSON with this structure:
{
    "schedule": [
        {
            "day": 1,
            "date": "2024-01-15",
            "topics": ["Topic 1", "Topic 2"],
            "hours": 3,
            "type": "learning|revision|practice|mock_test",
            "tips": "Focus on..."
        }
    ],
    "revision_dates": ["2024-01-20", "2024-01-25"],
    "mock_test_dates": ["2024-01-28"],
    "strategy": "Brief strategy description"
}"""},
        ]

        if context:
            messages.append({
                "role": "system",
                "content": f"COURSE CONTENT:\n{context}"
            })

        prompt = f"""Create a study plan with:
- {hours_per_day} hours available per day
- {days_until_exam} days until exam
- Include revision days (spaced repetition)
- Include mock test days
- Prioritize difficult topics earlier
- Plan lighter study on revision days"""

        if topics:
            prompt += f"\n\nTopics to cover: {[t.get('name', t.get('topic', '')) for t in topics]}"

        messages.append({"role": "user", "content": prompt})

        return json_completion(messages, temperature=0.4)

    def analyze_progress(
        self,
        course_id: int,
        progress_data: List[Dict[str, Any]],
        quiz_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze student progress and provide insights."""
        messages = [
            {"role": "system", "content": ANALYTICS_AGENT_PROMPT + """
            
Output MUST be valid JSON:
{
    "readiness_score": 75,
    "insights": ["insight 1", "insight 2"],
    "weak_areas": ["topic 1"],
    "recommendations": ["recommendation 1"],
    "study_tips": ["tip 1"]
}"""},
            {"role": "user", "content": f"""Analyze this student's progress:

Progress Data: {progress_data[:20]}

Quiz Results: {quiz_data[:10]}

Provide actionable insights and recommendations."""}
        ]

        return json_completion(messages, temperature=0.3)


# Singleton
orchestrator = AgentOrchestrator()
