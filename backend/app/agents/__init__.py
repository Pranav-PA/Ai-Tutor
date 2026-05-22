"""Agent registry and initialization."""
from app.agents.base import BaseAgent, AgentContext, AgentResult, AgentStatus
from app.agents.runtime import (
    AgentRuntime, LearningPhase, HiCLaw, HiCLawRule,
    create_default_runtime, create_default_hiclaw
)
from app.agents.ingestion_agent import IngestionAgent
from app.agents.knowledge_agent import KnowledgeExtractionAgent
from app.agents.weightage_agent import WeightageAnalysisAgent
from app.agents.roadmap_agent import RoadmapAgent
from app.agents.teaching_agent import TeachingAgent
from app.agents.doubt_agent import DoubtAgent
from app.agents.quiz_agent import QuizAgent
from app.agents.evaluation_agent import EvaluationAgent
from app.agents.adaptive_agent import AdaptiveAgent


def create_agent_runtime() -> AgentRuntime:
    """Create and configure the full agent runtime."""
    runtime = create_default_runtime()

    # Register all agents
    runtime.register_agent(IngestionAgent(), LearningPhase.INGESTION)
    runtime.register_agent(KnowledgeExtractionAgent(), LearningPhase.KNOWLEDGE_EXTRACTION)
    runtime.register_agent(WeightageAnalysisAgent(), LearningPhase.WEIGHTAGE_ANALYSIS)
    runtime.register_agent(RoadmapAgent(), LearningPhase.ROADMAP_GENERATION)
    runtime.register_agent(TeachingAgent(), LearningPhase.TEACHING)
    runtime.register_agent(DoubtAgent(), LearningPhase.DOUBT_RESOLUTION)
    runtime.register_agent(QuizAgent(), LearningPhase.QUIZ)
    runtime.register_agent(EvaluationAgent(), LearningPhase.EVALUATION)
    runtime.register_agent(AdaptiveAgent(), LearningPhase.ADAPTATION)

    return runtime


# Global runtime instance
agent_runtime = create_agent_runtime()

__all__ = [
    "BaseAgent", "AgentContext", "AgentResult", "AgentStatus",
    "AgentRuntime", "LearningPhase", "HiCLaw", "HiCLawRule",
    "IngestionAgent", "KnowledgeExtractionAgent",
    "WeightageAnalysisAgent", "RoadmapAgent",
    "TeachingAgent", "DoubtAgent", "QuizAgent",
    "EvaluationAgent", "AdaptiveAgent",
    "agent_runtime", "create_agent_runtime",
]
