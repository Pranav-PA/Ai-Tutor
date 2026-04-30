"""
AgentScope - Base agent framework for the AI Learning Engine.

Implements:
- Base Agent class
- AgentScope Runtime (orchestration engine)
- HiCLaw (Hierarchical Control Logic for agent workflows)
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import structlog

logger = structlog.get_logger()


class AgentStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"


@dataclass
class AgentContext:
    """Shared context passed between agents."""
    user_id: str = ""
    course_id: str = ""
    topic_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def set(self, key: str, value: Any):
        self.data[key] = value
        self.history.append({
            "action": "set",
            "key": key,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "course_id": self.course_id,
            "topic_id": self.topic_id,
            "data": self.data,
            "metadata": self.metadata,
        }


@dataclass
class AgentResult:
    """Result returned by an agent after execution."""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    next_agent: Optional[str] = None  # Suggested next agent
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.status = AgentStatus.IDLE
        self._logger = structlog.get_logger(agent=name)

    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the agent's main logic."""
        pass

    async def pre_execute(self, context: AgentContext) -> bool:
        """Pre-execution hook. Return False to skip execution."""
        self.status = AgentStatus.RUNNING
        self._logger.info("agent_starting", context_keys=list(context.data.keys()))
        return True

    async def post_execute(self, context: AgentContext, result: AgentResult):
        """Post-execution hook."""
        self.status = AgentStatus.COMPLETED if result.success else AgentStatus.FAILED
        self._logger.info(
            "agent_completed",
            success=result.success,
            error=result.error
        )

    async def run(self, context: AgentContext) -> AgentResult:
        """Full execution pipeline with hooks."""
        try:
            should_run = await self.pre_execute(context)
            if not should_run:
                return AgentResult(success=True, data={"skipped": True})

            result = await self.execute(context)
            await self.post_execute(context, result)
            return result
        except Exception as e:
            self.status = AgentStatus.FAILED
            self._logger.error("agent_error", error=str(e))
            return AgentResult(success=False, error=str(e))
