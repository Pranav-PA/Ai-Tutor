"""Weightage Analysis Agent - Parses PYQs and assigns importance scores."""
from typing import Dict, List, Any

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.services import llm_service


class WeightageAnalysisAgent(BaseAgent):
    """
    Analyzes previous year questions to determine topic importance.
    
    Responsibilities:
    - Parse PYQ content
    - Detect question frequency per topic
    - Assign importance scores
    - Identify high-yield topics
    """

    def __init__(self):
        super().__init__(
            name="weightage_analysis_agent",
            description="Analyzes PYQ patterns and assigns topic importance scores"
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """Analyze PYQ weightage."""
        knowledge_structure = context.get("knowledge_extraction_agent.knowledge_structure", {})
        pyq_text = context.get("knowledge_extraction_agent.pyq_text", "")

        if not knowledge_structure:
            return AgentResult(success=False, error="No knowledge structure available")

        # Extract topic list
        topics = []
        for unit in knowledge_structure.get("units", []):
            for topic in unit.get("topics", []):
                topics.append(topic["title"])

        # Analyze PYQ weightage
        if pyq_text:
            weightage = await self._analyze_pyq_weightage(topics, pyq_text)
        else:
            # Default weightage if no PYQs
            weightage = {topic: {"frequency": 0, "importance": 0.5} for topic in topics}

        # Enrich knowledge structure with weightage
        enriched_structure = self._apply_weightage(knowledge_structure, weightage)

        return AgentResult(
            success=True,
            data={
                "weightage": weightage,
                "enriched_structure": enriched_structure,
            },
            next_agent="roadmap_agent"
        )

    async def _analyze_pyq_weightage(
        self, topics: List[str], pyq_text: str
    ) -> Dict[str, Dict]:
        """Use LLM to analyze PYQ frequency and importance."""
        system_prompt = """You are an expert exam analyst. Analyze the previous year 
        questions and determine how often each topic appears and its importance.
        
        Return a JSON object:
        {
            "analysis": [
                {
                    "topic": "Topic Name",
                    "frequency": 5,
                    "importance": 0.85,
                    "question_types": ["mcq", "short_answer", "long_answer"],
                    "marks_distribution": "high|medium|low"
                }
            ]
        }
        
        frequency = number of times topic appeared in PYQs
        importance = 0.0 to 1.0 score based on frequency and marks weight"""

        prompt = f"""Topics to analyze:
{chr(10).join(f'- {t}' for t in topics)}

Previous Year Questions:
{pyq_text[:6000]}

Analyze the frequency and importance of each topic based on these PYQs."""

        result = await llm_service.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=3000
        )

        # Convert to lookup dict
        weightage = {}
        for item in result.get("analysis", []):
            weightage[item["topic"]] = {
                "frequency": item.get("frequency", 0),
                "importance": item.get("importance", 0.5),
                "question_types": item.get("question_types", []),
                "marks_distribution": item.get("marks_distribution", "medium"),
            }

        # Fill in missing topics
        for topic in topics:
            if topic not in weightage:
                weightage[topic] = {"frequency": 0, "importance": 0.5}

        return weightage

    def _apply_weightage(
        self, structure: Dict, weightage: Dict
    ) -> Dict:
        """Apply weightage scores to the knowledge structure."""
        enriched = structure.copy()

        for unit in enriched.get("units", []):
            unit_importance = 0
            topic_count = 0
            for topic in unit.get("topics", []):
                topic_name = topic["title"]
                if topic_name in weightage:
                    w = weightage[topic_name]
                    topic["importance_score"] = w.get("importance", 0.5)
                    topic["pyq_frequency"] = w.get("frequency", 0)
                    topic["question_types"] = w.get("question_types", [])
                    unit_importance += topic["importance_score"]
                    topic_count += 1

            unit["importance_score"] = unit_importance / max(topic_count, 1)

        return enriched
