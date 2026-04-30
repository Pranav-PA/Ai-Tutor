"""
AgentScope Runtime - Orchestration engine for agent execution.

Manages:
- Agent registration
- Execution flow
- Context passing
- State machine for learning lifecycle
"""
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
from dataclasses import dataclass, field

import structlog

from app.agents.base import BaseAgent, AgentContext, AgentResult, AgentStatus

logger = structlog.get_logger()


class LearningPhase(str, Enum):
    """Learning lifecycle states."""
    INGESTION = "ingestion"
    KNOWLEDGE_EXTRACTION = "knowledge_extraction"
    WEIGHTAGE_ANALYSIS = "weightage_analysis"
    ROADMAP_GENERATION = "roadmap_generation"
    TEACHING = "teaching"
    DOUBT_RESOLUTION = "doubt_resolution"
    QUIZ = "quiz"
    EVALUATION = "evaluation"
    ADAPTATION = "adaptation"


@dataclass
class TransitionRule:
    """Defines when to transition between phases."""
    from_phase: LearningPhase
    to_phase: LearningPhase
    condition: Optional[Callable[[AgentContext], bool]] = None
    priority: int = 0


class AgentRuntime:
    """
    AgentScope Runtime - manages agent lifecycle and orchestration.
    
    Implements a state machine for the learning lifecycle,
    routing execution to appropriate agents based on current phase.
    """

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._phase_agents: Dict[LearningPhase, str] = {}
        self._transitions: List[TransitionRule] = []
        self._current_phase: LearningPhase = LearningPhase.INGESTION
        self._logger = structlog.get_logger(component="runtime")

    def register_agent(self, agent: BaseAgent, phase: Optional[LearningPhase] = None):
        """Register an agent with the runtime."""
        self._agents[agent.name] = agent
        if phase:
            self._phase_agents[phase] = agent.name
        self._logger.info("agent_registered", name=agent.name, phase=phase)

    def add_transition(self, rule: TransitionRule):
        """Add a state transition rule."""
        self._transitions.append(rule)
        self._transitions.sort(key=lambda r: r.priority, reverse=True)

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get a registered agent by name."""
        return self._agents.get(name)

    async def execute_agent(self, agent_name: str, context: AgentContext) -> AgentResult:
        """Execute a specific agent by name."""
        agent = self._agents.get(agent_name)
        if not agent:
            return AgentResult(success=False, error=f"Agent '{agent_name}' not found")

        self._logger.info("executing_agent", agent=agent_name)
        result = await agent.run(context)

        # Update context with result data
        for key, value in result.data.items():
            context.set(f"{agent_name}.{key}", value)

        return result

    async def execute_phase(self, phase: LearningPhase, context: AgentContext) -> AgentResult:
        """Execute the agent associated with a learning phase."""
        agent_name = self._phase_agents.get(phase)
        if not agent_name:
            return AgentResult(success=False, error=f"No agent for phase '{phase}'")

        self._current_phase = phase
        return await self.execute_agent(agent_name, context)

    async def execute_pipeline(
        self,
        phases: List[LearningPhase],
        context: AgentContext
    ) -> Dict[str, AgentResult]:
        """Execute a sequence of phases."""
        results = {}
        for phase in phases:
            result = await self.execute_phase(phase, context)
            results[phase.value] = result
            if not result.success:
                self._logger.error("pipeline_failed", phase=phase, error=result.error)
                break
        return results

    def get_next_phase(self, context: AgentContext) -> Optional[LearningPhase]:
        """Determine next phase based on transition rules."""
        for rule in self._transitions:
            if rule.from_phase == self._current_phase:
                if rule.condition is None or rule.condition(context):
                    return rule.to_phase
        return None

    async def execute_adaptive_loop(self, context: AgentContext) -> List[AgentResult]:
        """Execute the adaptive learning loop until completion or manual stop."""
        results = []
        max_iterations = 50  # Safety limit

        for _ in range(max_iterations):
            next_phase = self.get_next_phase(context)
            if next_phase is None:
                break

            result = await self.execute_phase(next_phase, context)
            results.append(result)

            if not result.success:
                break

            # Check for explicit stop signal
            if context.get("stop_loop", False):
                break

        return results


# ─── HiCLaw - Hierarchical Control Logic ──────────────────────────────────────

class HiCLawPriority(str, Enum):
    """Priority levels for HiCLaw rules."""
    CRITICAL = "critical"  # Must execute (e.g., safety checks)
    HIGH = "high"          # Strong recommendation
    MEDIUM = "medium"      # Normal flow
    LOW = "low"            # Optional enhancement


@dataclass
class HiCLawRule:
    """A hierarchical control rule for agent decision-making."""
    name: str
    priority: HiCLawPriority
    condition: Callable[[AgentContext], bool]
    action: str  # Agent name or action to trigger
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class HiCLaw:
    """
    Hierarchical Control Logic for Agent Workflows.
    
    Manages decision hierarchy and agent triggering rules.
    Higher priority rules override lower priority ones.
    """

    def __init__(self):
        self._rules: List[HiCLawRule] = []
        self._logger = structlog.get_logger(component="hiclaw")

    def add_rule(self, rule: HiCLawRule):
        """Add a control rule."""
        self._rules.append(rule)
        self._rules.sort(
            key=lambda r: list(HiCLawPriority).index(r.priority)
        )

    def evaluate(self, context: AgentContext) -> List[HiCLawRule]:
        """Evaluate all rules and return matching ones in priority order."""
        matching = []
        for rule in self._rules:
            try:
                if rule.condition(context):
                    matching.append(rule)
                    self._logger.info("rule_matched", rule=rule.name, priority=rule.priority)
            except Exception as e:
                self._logger.error("rule_evaluation_error", rule=rule.name, error=str(e))
        return matching

    def get_action(self, context: AgentContext) -> Optional[str]:
        """Get the highest priority action to execute."""
        matching = self.evaluate(context)
        if matching:
            return matching[0].action
        return None

    def get_all_actions(self, context: AgentContext) -> List[str]:
        """Get all applicable actions in priority order."""
        matching = self.evaluate(context)
        return [rule.action for rule in matching]


# ─── Default Runtime & HiCLaw Setup ──────────────────────────────────────


def create_default_hiclaw() -> HiCLaw:
    """Create the default HiCLaw rules for the learning engine."""
    hiclaw = HiCLaw()

    # Critical: If quiz score < 40%, force revision
    hiclaw.add_rule(HiCLawRule(
        name="force_revision_on_low_score",
        priority=HiCLawPriority.CRITICAL,
        condition=lambda ctx: ctx.get("last_quiz_score", 100) < 40,
        action="revision",
        description="Force revision when quiz score is critically low"
    ))

    # High: If quiz score < 60%, suggest revision
    hiclaw.add_rule(HiCLawRule(
        name="suggest_revision_on_medium_score",
        priority=HiCLawPriority.HIGH,
        condition=lambda ctx: 40 <= ctx.get("last_quiz_score", 100) < 60,
        action="adaptive_revision",
        description="Suggest revision for weak areas when score is below threshold"
    ))

    # Medium: Normal progression
    hiclaw.add_rule(HiCLawRule(
        name="continue_learning",
        priority=HiCLawPriority.MEDIUM,
        condition=lambda ctx: ctx.get("last_quiz_score", 0) >= 60,
        action="next_topic",
        description="Continue to next topic when score is satisfactory"
    ))

    # High: Level up on excellent performance
    hiclaw.add_rule(HiCLawRule(
        name="level_up_on_excellence",
        priority=HiCLawPriority.HIGH,
        condition=lambda ctx: ctx.get("last_quiz_score", 0) >= 90 and ctx.get("consecutive_high_scores", 0) >= 3,
        action="level_up",
        description="Increase difficulty on consistently high performance"
    ))

    # Medium: Check if all topics completed
    hiclaw.add_rule(HiCLawRule(
        name="course_completion_check",
        priority=HiCLawPriority.MEDIUM,
        condition=lambda ctx: ctx.get("topics_completed", 0) >= ctx.get("topics_total", 1),
        action="course_complete",
        description="Mark course as complete when all topics are done"
    ))

    return hiclaw


def create_default_runtime() -> AgentRuntime:
    """Create runtime with default transition rules."""
    runtime = AgentRuntime()

    # Define state transitions
    transitions = [
        TransitionRule(
            from_phase=LearningPhase.INGESTION,
            to_phase=LearningPhase.KNOWLEDGE_EXTRACTION,
            priority=10
        ),
        TransitionRule(
            from_phase=LearningPhase.KNOWLEDGE_EXTRACTION,
            to_phase=LearningPhase.WEIGHTAGE_ANALYSIS,
            priority=10
        ),
        TransitionRule(
            from_phase=LearningPhase.WEIGHTAGE_ANALYSIS,
            to_phase=LearningPhase.ROADMAP_GENERATION,
            priority=10
        ),
        TransitionRule(
            from_phase=LearningPhase.ROADMAP_GENERATION,
            to_phase=LearningPhase.TEACHING,
            priority=10
        ),
        TransitionRule(
            from_phase=LearningPhase.TEACHING,
            to_phase=LearningPhase.QUIZ,
            condition=lambda ctx: ctx.get("teaching_complete", False),
            priority=10
        ),
        TransitionRule(
            from_phase=LearningPhase.QUIZ,
            to_phase=LearningPhase.EVALUATION,
            condition=lambda ctx: ctx.get("quiz_submitted", False),
            priority=10
        ),
        TransitionRule(
            from_phase=LearningPhase.EVALUATION,
            to_phase=LearningPhase.ADAPTATION,
            priority=10
        ),
        TransitionRule(
            from_phase=LearningPhase.ADAPTATION,
            to_phase=LearningPhase.TEACHING,
            condition=lambda ctx: ctx.get("adaptive_action") == "continue",
            priority=5
        ),
        TransitionRule(
            from_phase=LearningPhase.ADAPTATION,
            to_phase=LearningPhase.TEACHING,
            condition=lambda ctx: ctx.get("adaptive_action") == "revise",
            priority=5
        ),
    ]

    for transition in transitions:
        runtime.add_transition(transition)

    return runtime
