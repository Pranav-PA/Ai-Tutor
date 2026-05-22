"""Adaptive Agent - Decides learning path adjustments based on performance."""
from typing import Dict, List, Any, Optional

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.agents.runtime import HiCLaw, create_default_hiclaw


class AdaptiveAgent(BaseAgent):
    """
    Makes adaptive decisions about the learning path.
    
    Responsibilities:
    - Analyze performance data
    - Decide: Revise OR Continue
    - Adjust difficulty level
    - Identify revision topics
    - Use HiCLaw rules for decision hierarchy
    """

    def __init__(self):
        super().__init__(
            name="adaptive_agent",
            description="Adapts learning path based on student performance"
        )
        self.hiclaw = create_default_hiclaw()

    async def execute(self, context: AgentContext) -> AgentResult:
        """Make adaptive learning decisions."""
        # Get evaluation data
        percentage = context.get("evaluation_agent.percentage", 0)
        weak_areas = context.get("evaluation_agent.weak_areas", [])
        current_difficulty = context.get("current_difficulty", "intermediate")
        topics_completed = context.get("topics_completed", 0)
        topics_total = context.get("topics_total", 0)
        consecutive_high = context.get("consecutive_high_scores", 0)

        # Update context for HiCLaw evaluation
        context.set("last_quiz_score", percentage)
        context.set("consecutive_high_scores", consecutive_high)
        context.set("topics_completed", topics_completed)
        context.set("topics_total", topics_total)

        # Use HiCLaw to determine action
        action = self.hiclaw.get_action(context)

        # Make detailed recommendation
        recommendation = await self._make_recommendation(
            action=action,
            percentage=percentage,
            weak_areas=weak_areas,
            current_difficulty=current_difficulty,
            topics_completed=topics_completed,
            topics_total=topics_total,
        )

        return AgentResult(
            success=True,
            data={
                "action": action or "continue",
                "recommendation": recommendation,
                "percentage": percentage,
                "weak_areas": weak_areas,
            }
        )

    async def _make_recommendation(
        self,
        action: Optional[str],
        percentage: float,
        weak_areas: List[Dict],
        current_difficulty: str,
        topics_completed: int,
        topics_total: int,
    ) -> Dict[str, Any]:
        """Generate a detailed recommendation."""
        recommendation = {
            "action": action or "continue",
            "reasoning": "",
            "difficulty_adjustment": None,
            "revision_topics": [],
            "next_steps": [],
        }

        if action == "revision":
            recommendation["reasoning"] = (
                f"Your score ({percentage}%) indicates significant gaps. "
                "Let's revisit the weak areas before moving forward."
            )
            recommendation["revision_topics"] = [
                w.get("topic", "") for w in weak_areas
            ]
            recommendation["next_steps"] = [
                "Review the concepts you struggled with",
                "Focus on understanding, not memorization",
                "Retake the quiz after revision",
            ]

        elif action == "adaptive_revision":
            recommendation["reasoning"] = (
                f"Your score ({percentage}%) shows some understanding but room for improvement. "
                "Let's strengthen specific areas."
            )
            recommendation["revision_topics"] = [
                w.get("topic", "") for w in weak_areas[:3]
            ]
            recommendation["next_steps"] = [
                "Quick review of weak areas",
                "Practice targeted questions",
                "Then continue to next topic",
            ]

        elif action == "level_up":
            new_difficulty = self._next_difficulty(current_difficulty)
            recommendation["reasoning"] = (
                f"Excellent performance ({percentage}%)! "
                f"Increasing difficulty to {new_difficulty}."
            )
            recommendation["difficulty_adjustment"] = new_difficulty
            recommendation["next_steps"] = [
                f"Moving to {new_difficulty} level content",
                "More challenging questions ahead",
                "Keep up the great work!",
            ]

        elif action == "course_complete":
            recommendation["reasoning"] = (
                f"Congratulations! You've completed all {topics_total} topics!"
            )
            recommendation["next_steps"] = [
                "Review any remaining weak areas",
                "Take a comprehensive final test",
                "Celebrate your achievement!",
            ]

        else:  # continue / next_topic
            recommendation["reasoning"] = (
                f"Good performance ({percentage}%). Moving to the next topic."
            )
            recommendation["next_steps"] = [
                "Proceeding to the next topic in your roadmap",
                f"Progress: {topics_completed}/{topics_total} topics",
            ]

        return recommendation

    def _next_difficulty(self, current: str) -> str:
        """Get the next difficulty level."""
        levels = ["beginner", "intermediate", "advanced"]
        idx = levels.index(current) if current in levels else 1
        return levels[min(idx + 1, len(levels) - 1)]
