"""Doubt Agent - Context-aware Q&A using vector retrieval."""
from typing import Dict, List, Any

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.services import llm_service, vector_store


class DoubtAgent(BaseAgent):
    """
    Context-aware doubt resolution agent.
    
    Responsibilities:
    - Accept student questions
    - Retrieve relevant context from vector store
    - Generate accurate answers grounded in course material
    - Track conversation context for follow-up questions
    """

    def __init__(self):
        super().__init__(
            name="doubt_agent",
            description="Context-aware Q&A for student doubts"
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """Resolve a student's doubt."""
        course_id = context.course_id
        question = context.get("question", "")
        topic_title = context.get("topic_title", "")
        chat_history = context.get("chat_history", [])

        if not question:
            return AgentResult(success=False, error="No question provided")

        # Retrieve relevant content
        search_query = f"{topic_title}: {question}" if topic_title else question
        relevant_content = await vector_store.search(
            course_id=course_id,
            query=search_query,
            top_k=6
        )

        # Build context
        source_content = "\n\n".join([
            f"[Source: {meta.get('filename', 'unknown')}]\n{text}"
            for text, score, meta in relevant_content if score > 0.25
        ])

        # Generate answer
        answer = await self._answer_doubt(
            question, topic_title, source_content, chat_history
        )

        return AgentResult(
            success=True,
            data={
                "answer": answer,
                "sources_used": [
                    {"text": text[:200], "score": score, "file": meta.get("filename", "")}
                    for text, score, meta in relevant_content[:3]
                ],
            }
        )

    async def _answer_doubt(
        self,
        question: str,
        topic: str,
        source: str,
        history: List[Dict]
    ) -> str:
        """Generate an answer to the student's doubt."""
        system_prompt = """You are a helpful tutor answering student doubts.

Rules:
1. Answer ONLY based on the provided source material
2. If the answer isn't in the sources, say so honestly
3. Be clear and concise
4. Use examples when helpful
5. If it's a follow-up question, consider the chat history"""

        history_str = ""
        if history:
            recent = history[-6:]  # Last 3 exchanges
            history_str = "\nPrevious conversation:\n"
            for msg in recent:
                history_str += f"{msg['role'].title()}: {msg['content']}\n"

        prompt = f"""Topic: {topic}
{history_str}
Student's Question: {question}

Source Material:
{source[:4000]}

Provide a clear, helpful answer:"""

        return await llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.4,
            max_tokens=1500,
            use_cache=False  # Doubts are contextual, don't cache
        )
