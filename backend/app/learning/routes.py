"""Learning routes - Topic content, teaching, and navigation."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.auth.security import get_current_user
from app.models import (
    User, Course, Unit, Topic, Subtopic,
    UserProgress, TopicStatus, Roadmap, LearningState
)
from app.schemas import (
    UnitResponse, TopicResponse, ProgressUpdate,
    ProgressResponse, RoadmapResponse, LearningStateResponse
)
from app.agents import agent_runtime, AgentContext

router = APIRouter(prefix="/learning", tags=["Learning"])


@router.get("/courses/{course_id}/roadmap", response_model=RoadmapResponse)
async def get_roadmap(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the learning roadmap for a course."""
    result = await db.execute(
        select(Roadmap).where(Roadmap.course_id == course_id)
    )
    roadmap = result.scalar_one_or_none()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not generated yet. Process the course first.")
    return roadmap


@router.get("/courses/{course_id}/units")
async def get_units(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get all units for a course with their topics."""
    result = await db.execute(
        select(Unit)
        .where(Unit.course_id == course_id)
        .options(selectinload(Unit.topics).selectinload(Topic.subtopics))
        .order_by(Unit.order_index)
    )
    units = result.scalars().all()
    return units


@router.get("/topics/{topic_id}")
async def get_topic_content(
    topic_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get full teaching content for a topic."""
    result = await db.execute(
        select(Topic)
        .where(Topic.id == topic_id)
        .options(selectinload(Topic.subtopics))
    )
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # If content not generated yet, generate it
    if not topic.content:
        # Get course_id through unit
        result = await db.execute(select(Unit).where(Unit.id == topic.unit_id))
        unit = result.scalar_one_or_none()

        context = AgentContext(
            user_id=str(current_user.id),
            course_id=str(unit.course_id),
            topic_id=str(topic_id),
        )
        context.set("topic_title", topic.title)
        context.set("topic_description", topic.description or "")
        context.set("difficulty", topic.difficulty.value if topic.difficulty else "intermediate")
        context.set("subtopics", [st.title for st in topic.subtopics])

        # Execute teaching agent
        teaching_agent = agent_runtime.get_agent("teaching_agent")
        result_agent = await teaching_agent.run(context)

        if result_agent.success:
            topic.content = result_agent.data.get("explanation", "")
            topic.key_points = result_agent.data.get("key_points", [])
            topic.examples = result_agent.data.get("examples", [])
            topic.memory_tricks = result_agent.data.get("memory_tricks", [])
            await db.commit()

    # Update progress
    await _update_progress(db, current_user.id, topic_id, TopicStatus.IN_PROGRESS)

    return {
        "id": str(topic.id),
        "title": topic.title,
        "description": topic.description,
        "content": topic.content,
        "difficulty": topic.difficulty,
        "key_points": topic.key_points,
        "examples": topic.examples,
        "memory_tricks": topic.memory_tricks,
        "importance_score": topic.importance_score,
        "estimated_minutes": topic.estimated_minutes,
        "subtopics": [{"id": str(st.id), "title": st.title, "content": st.content} for st in topic.subtopics],
    }


@router.post("/topics/{topic_id}/complete")
async def mark_topic_complete(
    topic_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a topic as completed."""
    await _update_progress(db, current_user.id, topic_id, TopicStatus.COMPLETED)
    return {"status": "completed", "topic_id": topic_id}


@router.get("/courses/{course_id}/progress")
async def get_course_progress(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get progress overview for a course."""
    # Get all topics
    result = await db.execute(
        select(Topic).join(Unit).where(Unit.course_id == course_id)
    )
    all_topics = result.scalars().all()
    topic_ids = [t.id for t in all_topics]

    # Get progress records
    result = await db.execute(
        select(UserProgress).where(
            UserProgress.user_id == current_user.id,
            UserProgress.topic_id.in_(topic_ids)
        )
    )
    progress_records = result.scalars().all()

    progress_map = {str(p.topic_id): p for p in progress_records}

    return {
        "total_topics": len(all_topics),
        "completed": sum(1 for p in progress_records if p.status == TopicStatus.COMPLETED),
        "in_progress": sum(1 for p in progress_records if p.status == TopicStatus.IN_PROGRESS),
        "not_started": len(all_topics) - len(progress_records),
        "average_score": (
            sum(p.score for p in progress_records) / len(progress_records)
            if progress_records else 0
        ),
        "topics": [
            {
                "topic_id": str(t.id),
                "title": t.title,
                "status": progress_map.get(str(t.id), None) and progress_map[str(t.id)].status.value or "not_started",
                "score": progress_map.get(str(t.id), None) and progress_map[str(t.id)].score or 0,
            }
            for t in all_topics
        ],
    }


@router.get("/courses/{course_id}/next-topic")
async def get_next_topic(
    course_id: str,
    current_topic_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the next recommended topic."""
    result = await db.execute(
        select(Topic)
        .join(Unit)
        .where(Unit.course_id == course_id)
        .order_by(Unit.order_index, Topic.order_index)
    )
    topics = result.scalars().all()

    if not topics:
        raise HTTPException(status_code=404, detail="No topics found")

    if current_topic_id:
        # Find current and return next
        for i, topic in enumerate(topics):
            if str(topic.id) == current_topic_id and i + 1 < len(topics):
                return {"next_topic_id": str(topics[i + 1].id), "title": topics[i + 1].title}

    # Return first uncompleted topic
    result = await db.execute(
        select(UserProgress).where(
            UserProgress.user_id == current_user.id,
            UserProgress.status == TopicStatus.COMPLETED,
        )
    )
    completed_ids = {str(p.topic_id) for p in result.scalars().all()}

    for topic in topics:
        if str(topic.id) not in completed_ids:
            return {"next_topic_id": str(topic.id), "title": topic.title}

    return {"next_topic_id": None, "title": "All topics completed!"}


async def _update_progress(db: AsyncSession, user_id, topic_id: str, status: TopicStatus):
    """Create or update progress record."""
    result = await db.execute(
        select(UserProgress).where(
            UserProgress.user_id == user_id,
            UserProgress.topic_id == topic_id,
        )
    )
    progress = result.scalar_one_or_none()

    if progress:
        progress.status = status
        if status == TopicStatus.COMPLETED:
            progress.attempts += 1
    else:
        progress = UserProgress(
            user_id=user_id,
            topic_id=topic_id,
            status=status,
        )
        db.add(progress)

    await db.commit()
