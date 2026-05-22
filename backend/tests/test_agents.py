"""Tests for the agent system."""
import pytest
from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.agents.runtime import (
    AgentRuntime, LearningPhase, HiCLaw, HiCLawRule, HiCLawPriority,
    create_default_hiclaw, create_default_runtime
)


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    def __init__(self, name="mock", return_data=None):
        super().__init__(name=name)
        self.return_data = return_data or {}

    async def execute(self, context: AgentContext) -> AgentResult:
        return AgentResult(success=True, data=self.return_data)


@pytest.mark.asyncio
async def test_agent_execution():
    """Test basic agent execution."""
    agent = MockAgent(return_data={"key": "value"})
    context = AgentContext(user_id="test-user", course_id="test-course")
    
    result = await agent.run(context)
    
    assert result.success is True
    assert result.data["key"] == "value"


@pytest.mark.asyncio
async def test_agent_context():
    """Test agent context operations."""
    context = AgentContext(user_id="u1", course_id="c1")
    
    context.set("key1", "value1")
    assert context.get("key1") == "value1"
    assert context.get("nonexistent", "default") == "default"
    assert len(context.history) == 1


@pytest.mark.asyncio
async def test_runtime_agent_registration():
    """Test agent registration in runtime."""
    runtime = AgentRuntime()
    agent = MockAgent("test_agent")
    
    runtime.register_agent(agent, LearningPhase.INGESTION)
    
    assert runtime.get_agent("test_agent") is agent


@pytest.mark.asyncio
async def test_runtime_execute_agent():
    """Test executing a specific agent through runtime."""
    runtime = AgentRuntime()
    agent = MockAgent("test_agent", {"result": 42})
    runtime.register_agent(agent)
    
    context = AgentContext()
    result = await runtime.execute_agent("test_agent", context)
    
    assert result.success is True
    assert result.data["result"] == 42


def test_hiclaw_rule_evaluation():
    """Test HiCLaw rule evaluation."""
    hiclaw = create_default_hiclaw()
    
    # Low score context
    context = AgentContext()
    context.set("last_quiz_score", 30)
    
    action = hiclaw.get_action(context)
    assert action == "revision"  # Critical rule fires


def test_hiclaw_high_score():
    """Test HiCLaw with high score."""
    hiclaw = create_default_hiclaw()
    
    context = AgentContext()
    context.set("last_quiz_score", 95)
    context.set("consecutive_high_scores", 4)
    
    action = hiclaw.get_action(context)
    assert action == "level_up"


def test_hiclaw_medium_score():
    """Test HiCLaw with medium score."""
    hiclaw = create_default_hiclaw()
    
    context = AgentContext()
    context.set("last_quiz_score", 50)
    context.set("consecutive_high_scores", 0)
    
    action = hiclaw.get_action(context)
    assert action == "adaptive_revision"


@pytest.mark.asyncio
async def test_pipeline_execution():
    """Test full pipeline execution."""
    runtime = AgentRuntime()
    runtime.register_agent(MockAgent("agent1", {"step": 1}), LearningPhase.INGESTION)
    runtime.register_agent(MockAgent("agent2", {"step": 2}), LearningPhase.KNOWLEDGE_EXTRACTION)
    
    context = AgentContext()
    results = await runtime.execute_pipeline(
        [LearningPhase.INGESTION, LearningPhase.KNOWLEDGE_EXTRACTION],
        context
    )
    
    assert len(results) == 2
    assert results["ingestion"].success is True
    assert results["knowledge_extraction"].success is True
