"""Roadmap Agent - Creates the learning path with priority ordering."""
from typing import Dict, List, Any

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.services import llm_service


class RoadmapAgent(BaseAgent):
    """
    Creates an optimized learning path.
    
    Responsibilities:
    - Order topics from Beginner → Advanced
    - Add priority tags based on PYQ weightage
    - Consider prerequisites
    - Estimate time requirements
    - Generate a navigable roadmap structure
    """

    def __init__(self):
        super().__init__(
            name="roadmap_agent",
            description="Creates optimized learning roadmap with priority ordering"
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """Generate learning roadmap."""
        enriched_structure = context.get("weightage_analysis_agent.enriched_structure", {})
        knowledge_structure = context.get("knowledge_extraction_agent.knowledge_structure", {})

        structure = enriched_structure or knowledge_structure
        if not structure:
            return AgentResult(success=False, error="No knowledge structure available")

        # Generate optimized roadmap
        roadmap = await self._generate_roadmap(structure)

        return AgentResult(
            success=True,
            data={
                "roadmap": roadmap,
            },
            next_agent="teaching_agent"
        )

    async def _generate_roadmap(self, structure: Dict) -> Dict[str, Any]:
        """Generate an optimized learning roadmap."""
        system_prompt = """You are an expert learning path designer. Given a knowledge 
        structure with importance scores and dependencies, create an optimized learning roadmap.
        
        Return a JSON object:
        {
            "roadmap": {
                "title": "Course Roadmap",
                "total_topics": 0,
                "estimated_hours": 0,
                "phases": [
                    {
                        "phase_name": "Foundation",
                        "description": "Core concepts",
                        "difficulty": "beginner",
                        "units": [
                            {
                                "unit_title": "Unit Name",
                                "topics": [
                                    {
                                        "title": "Topic Name",
                                        "priority": "high|medium|low",
                                        "difficulty": "beginner|intermediate|advanced",
                                        "estimated_minutes": 30,
                                        "importance_score": 0.8,
                                        "order": 1
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        Rules:
        1. Start with foundational/prerequisite topics
        2. Group related topics together  
        3. High importance (PYQ) topics should be covered early
        4. Progressive difficulty (beginner → advanced)
        5. Include estimated time for each topic"""

        prompt = f"""Create an optimized learning roadmap from this structure:

{str(structure)[:6000]}

Design the roadmap with:
- Progressive difficulty levels
- Priority-based ordering (high PYQ frequency = earlier)
- Prerequisite awareness
- Time estimates"""

        result = await llm_service.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,
            max_tokens=4000
        )

        roadmap = result.get("roadmap", result)

        # Calculate totals
        total_topics = 0
        total_minutes = 0
        for phase in roadmap.get("phases", []):
            for unit in phase.get("units", []):
                for topic in unit.get("topics", []):
                    total_topics += 1
                    total_minutes += topic.get("estimated_minutes", 30)

        roadmap["total_topics"] = total_topics
        roadmap["estimated_hours"] = round(total_minutes / 60, 1)

        return roadmap
