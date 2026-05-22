"""Knowledge Extraction Agent - Extracts units, topics, subtopics and builds dependency graph."""
from typing import Dict, List, Any

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.services import llm_service, vector_store


class KnowledgeExtractionAgent(BaseAgent):
    """
    Extracts structured knowledge from processed documents.
    
    Responsibilities:
    - Extract Units, Topics, Subtopics from syllabus and notes
    - Build dependency graph between topics
    - Identify prerequisites
    - Structure content hierarchically
    """

    def __init__(self):
        super().__init__(
            name="knowledge_extraction_agent",
            description="Extracts structured knowledge graph from documents"
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """Extract knowledge structure from documents."""
        course_id = context.course_id
        processed_docs = context.get("ingestion_agent.processed_documents", [])

        if not processed_docs:
            return AgentResult(success=False, error="No processed documents available")

        # Separate documents by type
        syllabus_text = ""
        notes_text = ""
        pyq_text = ""

        for doc in processed_docs:
            if doc["doc_type"] == "syllabus":
                syllabus_text += doc["extracted_text"] + "\n\n"
            elif doc["doc_type"] == "notes":
                notes_text += doc["extracted_text"] + "\n\n"
            elif doc["doc_type"] == "pyq":
                pyq_text += doc["extracted_text"] + "\n\n"

        # Extract structure using LLM
        knowledge_structure = await self._extract_structure(
            syllabus_text, notes_text
        )

        # Build dependency graph
        if knowledge_structure:
            dependencies = await self._build_dependencies(knowledge_structure)
            knowledge_structure["dependencies"] = dependencies

        return AgentResult(
            success=True,
            data={
                "knowledge_structure": knowledge_structure,
                "syllabus_text": syllabus_text,
                "notes_text": notes_text,
                "pyq_text": pyq_text,
            },
            next_agent="weightage_analysis_agent"
        )

    async def _extract_structure(self, syllabus: str, notes: str) -> Dict[str, Any]:
        """Use LLM to extract hierarchical structure."""
        system_prompt = """You are an expert curriculum analyst. Extract the complete 
        knowledge structure from the given syllabus and notes.
        
        Return a JSON object with this exact structure:
        {
            "units": [
                {
                    "title": "Unit Title",
                    "description": "Brief description",
                    "order": 1,
                    "topics": [
                        {
                            "title": "Topic Title",
                            "description": "Brief description",
                            "order": 1,
                            "difficulty": "beginner|intermediate|advanced",
                            "estimated_minutes": 30,
                            "subtopics": [
                                {
                                    "title": "Subtopic Title",
                                    "order": 1
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        Be thorough and extract ALL units, topics, and subtopics mentioned."""

        prompt = f"""Extract the complete knowledge structure from these documents:

SYLLABUS:
{syllabus[:4000]}

NOTES (excerpt):
{notes[:4000]}

Return the complete hierarchical structure as JSON."""

        result = await llm_service.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=4000
        )

        return result

    async def _build_dependencies(self, structure: Dict) -> List[Dict]:
        """Build dependency graph between topics."""
        topics = []
        for unit in structure.get("units", []):
            for topic in unit.get("topics", []):
                topics.append(topic["title"])

        if not topics:
            return []

        system_prompt = """You are an expert in curriculum design. Given a list of topics,
        identify prerequisite relationships between them.
        
        Return a JSON object:
        {
            "dependencies": [
                {"topic": "Topic B", "requires": ["Topic A"]},
                {"topic": "Topic C", "requires": ["Topic A", "Topic B"]}
            ]
        }
        
        Only include dependencies where one topic truly requires knowledge of another."""

        prompt = f"Topics: {', '.join(topics)}\n\nIdentify prerequisites:"

        result = await llm_service.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2
        )

        return result.get("dependencies", [])
