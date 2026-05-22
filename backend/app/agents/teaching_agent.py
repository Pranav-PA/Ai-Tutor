"""Teaching Agent - Explains concepts using uploaded data."""
from typing import Dict, List, Any

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.services import llm_service, vector_store


class TeachingAgent(BaseAgent):
    """
    Explains concepts using ONLY the uploaded course data.
    
    Responsibilities:
    - Generate clear explanations grounded in source material
    - Add examples from the notes
    - Create key points summaries
    - Generate memory tricks/mnemonics
    - Adapt explanation depth to difficulty level
    """

    def __init__(self):
        super().__init__(
            name="teaching_agent",
            description="Generates topic explanations grounded in uploaded materials"
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """Generate teaching content for a topic."""
        course_id = context.course_id
        topic_title = context.get("topic_title", "")
        topic_description = context.get("topic_description", "")
        difficulty = context.get("difficulty", "intermediate")
        subtopics = context.get("subtopics", [])

        if not topic_title:
            return AgentResult(success=False, error="No topic specified")

        # Retrieve relevant content from vector store
        relevant_content = await vector_store.search(
            course_id=course_id,
            query=f"{topic_title} {topic_description}",
            top_k=8
        )

        # Build context from retrieved documents
        source_content = "\n\n".join([text for text, score, meta in relevant_content if score > 0.3])

        # Generate comprehensive explanation
        explanation = await self._generate_explanation(
            topic_title, topic_description, subtopics, source_content, difficulty
        )

        # Generate key points
        key_points = await self._generate_key_points(topic_title, source_content)

        # Generate examples
        examples = await self._generate_examples(topic_title, source_content)

        # Generate memory tricks
        memory_tricks = await self._generate_memory_tricks(topic_title, key_points)

        return AgentResult(
            success=True,
            data={
                "explanation": explanation,
                "key_points": key_points,
                "examples": examples,
                "memory_tricks": memory_tricks,
                "source_context": source_content[:500],
            }
        )

    async def _generate_explanation(
        self,
        title: str,
        description: str,
        subtopics: List[str],
        source: str,
        difficulty: str
    ) -> str:
        """Generate a comprehensive topic explanation."""
        depth_guide = {
            "beginner": "Use simple language, lots of analogies, step-by-step explanations.",
            "intermediate": "Balanced depth, include technical details with clear explanations.",
            "advanced": "Deep technical content, advanced concepts, edge cases."
        }

        system_prompt = f"""You are an expert teacher. Explain topics clearly and thoroughly 
        using ONLY the provided source material. Do not add information not found in the sources.
        
        Difficulty Level: {difficulty}
        Teaching style: {depth_guide.get(difficulty, depth_guide['intermediate'])}
        
        Structure your explanation with:
        1. Introduction/Overview
        2. Core concepts explained
        3. Detailed breakdown of subtopics
        4. Connections between concepts
        5. Summary"""

        subtopics_str = "\n".join(f"- {st}" for st in subtopics) if subtopics else "N/A"

        prompt = f"""Explain the following topic comprehensively:

TOPIC: {title}
DESCRIPTION: {description}
SUBTOPICS:
{subtopics_str}

SOURCE MATERIAL:
{source[:5000]}

Generate a clear, well-structured explanation."""

        return await llm_service.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=3000
        )

    async def _generate_key_points(self, title: str, source: str) -> List[str]:
        """Generate key points for the topic."""
        prompt = f"""Extract 5-8 key points for the topic "{title}" from this content:

{source[:3000]}

Return as JSON: {{"key_points": ["point 1", "point 2", ...]}}"""

        result = await llm_service.generate_json(
            prompt=prompt,
            system_prompt="Extract concise, memorable key points.",
            temperature=0.3
        )
        return result.get("key_points", [])

    async def _generate_examples(self, title: str, source: str) -> List[Dict]:
        """Generate practical examples."""
        prompt = f"""Generate 2-3 practical examples for "{title}" based on this content:

{source[:3000]}

Return as JSON: {{"examples": [{{"title": "Example 1", "content": "detailed example"}}]}}"""

        result = await llm_service.generate_json(
            prompt=prompt,
            system_prompt="Generate clear, practical examples that aid understanding.",
            temperature=0.5
        )
        return result.get("examples", [])

    async def _generate_memory_tricks(self, title: str, key_points: List[str]) -> List[str]:
        """Generate mnemonics and memory tricks."""
        prompt = f"""Generate 2-3 memory tricks/mnemonics for remembering the key concepts of "{title}":

Key Points:
{chr(10).join(f'- {p}' for p in key_points[:5])}

Return as JSON: {{"memory_tricks": ["trick 1", "trick 2"]}}"""

        result = await llm_service.generate_json(
            prompt=prompt,
            system_prompt="Create memorable mnemonics, acronyms, or memory aids.",
            temperature=0.7
        )
        return result.get("memory_tricks", [])
