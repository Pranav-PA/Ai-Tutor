"""Adaptive learning routes - Recommendations and doubt resolution."""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.security import get_current_user
from app.models import (
    User, Topic, Unit, ChatMessage, UserProgress,
    QuizAttempt, LearningState
)
from app.schemas import ChatRequest, ChatResponse, AdaptiveRecommendation
from app.agents import agent_runtime, AgentContext

router = APIRouter(prefix="/adaptive", tags=["Adaptive Learning"])


@router.post("/doubt")
async def ask_doubt(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Ask a doubt / question about the current topic."""
    # Get topic context if provided
    topic_title = ""
    course_id = ""
    if request.topic_id:
        result = await db.execute(select(Topic).where(Topic.id == request.topic_id))
        topic = result.scalar_one_or_none()
        if topic:
            topic_title = topic.title
            result = await db.execute(select(Unit).where(Unit.id == topic.unit_id))
            unit = result.scalar_one_or_none()
            if unit:
                course_id = str(unit.course_id)

    # Get chat history
    result = await db.execute(
        select(ChatMessage)
        .where(
            ChatMessage.user_id == current_user.id,
            ChatMessage.topic_id == request.topic_id,
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
    )
    history_records = result.scalars().all()
    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in reversed(history_records)
    ]

    # Execute Doubt Agent
    context = AgentContext(
        user_id=str(current_user.id),
        course_id=course_id,
        topic_id=str(request.topic_id) if request.topic_id else "",
    )
    context.set("question", request.message)
    context.set("topic_title", topic_title)
    context.set("chat_history", chat_history)

    doubt_agent = agent_runtime.get_agent("doubt_agent")
    result_agent = await doubt_agent.run(context)

    if not result_agent.success:
        raise HTTPException(status_code=500, detail="Failed to process doubt")

    answer = result_agent.data.get("answer", "I couldn't find an answer to that question.")

    # Save messages
    user_msg = ChatMessage(
        user_id=current_user.id,
        topic_id=request.topic_id,
        role="user",
        content=request.message,
    )
    assistant_msg = ChatMessage(
        user_id=current_user.id,
        topic_id=request.topic_id,
        role="assistant",
        content=answer,
        context_used=result_agent.data.get("sources_used"),
    )
    db.add(user_msg)
    db.add(assistant_msg)
    await db.commit()

    return {
        "answer": answer,
        "sources": result_agent.data.get("sources_used", []),
    }


@router.get("/recommend/{course_id}")
async def get_recommendation(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get adaptive learning recommendation."""
    # Get recent quiz attempts
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == current_user.id)
        .order_by(QuizAttempt.completed_at.desc())
        .limit(5)
    )
    recent_attempts = result.scalars().all()

    # Get progress stats
    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == current_user.id)
    )
    progress_records = result.scalars().all()

    # Calculate stats
    last_score = recent_attempts[0].percentage if recent_attempts else 0
    avg_score = (
        sum(a.percentage for a in recent_attempts) / len(recent_attempts)
        if recent_attempts else 0
    )
    consecutive_high = sum(1 for a in recent_attempts if a.percentage >= 80)
    topics_completed = sum(1 for p in progress_records if p.status.value == "completed")

    # Get total topics
    result = await db.execute(
        select(Topic).join(Unit).where(Unit.course_id == course_id)
    )
    total_topics = len(result.scalars().all())

    # Execute Adaptive Agent
    context = AgentContext(
        user_id=str(current_user.id),
        course_id=course_id,
    )
    context.set("evaluation_agent.percentage", last_score)
    context.set("evaluation_agent.weak_areas", 
        recent_attempts[0].weak_areas if recent_attempts else [])
    context.set("current_difficulty", "intermediate")
    context.set("topics_completed", topics_completed)
    context.set("topics_total", total_topics)
    context.set("consecutive_high_scores", consecutive_high)

    adaptive_agent = agent_runtime.get_agent("adaptive_agent")
    result_agent = await adaptive_agent.run(context)

    if not result_agent.success:
        return {"action": "continue", "recommendation": {"reasoning": "Continue learning"}}

    return {
        "action": result_agent.data.get("action", "continue"),
        "recommendation": result_agent.data.get("recommendation", {}),
        "stats": {
            "last_score": last_score,
            "average_score": avg_score,
            "topics_completed": topics_completed,
            "topics_total": total_topics,
        }
    }


@router.get("/analytics/{course_id}")
async def get_analytics(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed analytics for a course."""
    # Get all progress
    result = await db.execute(
        select(UserProgress)
        .join(Topic)
        .join(Unit)
        .where(
            Unit.course_id == course_id,
            UserProgress.user_id == current_user.id,
        )
    )
    progress_records = result.scalars().all()

    # Get quiz history
    result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == current_user.id)
        .order_by(QuizAttempt.completed_at.asc())
    )
    quiz_attempts = result.scalars().all()

    # Get topics
    result = await db.execute(
        select(Topic).join(Unit).where(Unit.course_id == course_id)
    )
    all_topics = result.scalars().all()
    topic_map = {str(t.id): t.title for t in all_topics}

    # Calculate analytics
    total_topics = len(all_topics)
    completed = sum(1 for p in progress_records if p.status.value == "completed")
    avg_score = (
        sum(p.score for p in progress_records) / len(progress_records)
        if progress_records else 0
    )
    total_time = sum(p.time_spent_minutes for p in progress_records)

    # Score history
    score_history = [
        {
            "date": a.completed_at.isoformat(),
            "score": a.percentage,
            "quiz_id": str(a.quiz_id),
        }
        for a in quiz_attempts
    ]

    # Identify weak/strong areas
    weak_areas = []
    strong_areas = []
    for p in progress_records:
        topic_name = topic_map.get(str(p.topic_id), "Unknown")
        if p.score < 60:
            weak_areas.append(topic_name)
        elif p.score >= 80:
            strong_areas.append(topic_name)

    # Topic performance
    topic_performance = [
        {
            "topic_id": str(p.topic_id),
            "topic": topic_map.get(str(p.topic_id), "Unknown"),
            "score": p.score,
            "status": p.status.value,
            "time_spent": p.time_spent_minutes,
            "attempts": p.attempts,
        }
        for p in progress_records
    ]

    return {
        "total_topics": total_topics,
        "completed_topics": completed,
        "completion_percentage": round(completed / max(total_topics, 1) * 100, 1),
        "average_score": round(avg_score, 1),
        "total_time_spent_minutes": total_time,
        "weak_areas": weak_areas,
        "strong_areas": strong_areas,
        "score_history": score_history,
        "topic_performance": topic_performance,
    }
