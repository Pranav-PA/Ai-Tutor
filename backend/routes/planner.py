"""Study planner routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database.connection import get_db
from backend.database.models import Course, Progress, StudySession
from backend.models.schemas import StudyPlanRequest, StudyPlanResponse
from backend.agents.orchestrator import orchestrator

router = APIRouter(prefix="/planner", tags=["planner"])


@router.post("/generate", response_model=StudyPlanResponse)
def generate_study_plan(request: StudyPlanRequest, db: Session = Depends(get_db)):
    """Generate a personalized study plan."""
    course = db.query(Course).filter(Course.id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Calculate days until exam
    exam_date = request.exam_date or course.exam_date
    if exam_date:
        days_until_exam = (exam_date - datetime.utcnow()).days
    else:
        days_until_exam = 30  # Default to 30 days

    # Get existing progress
    progress = db.query(Progress).filter(Progress.course_id == request.course_id).all()
    topics = [
        {"name": p.topic, "confidence": p.confidence, "is_weak": p.is_weak}
        for p in progress
    ]

    result = orchestrator.generate_study_plan(
        course_id=request.course_id,
        hours_per_day=request.hours_per_day,
        days_until_exam=days_until_exam,
        topics=topics if topics else None
    )

    return StudyPlanResponse(
        course_id=request.course_id,
        schedule=result.get("schedule", []),
        revision_dates=result.get("revision_dates", []),
        mock_test_dates=result.get("mock_test_dates", [])
    )


@router.post("/session/start")
def start_study_session(course_id: int, session_type: str = "learning", db: Session = Depends(get_db)):
    """Start a new study session."""
    session = StudySession(
        course_id=course_id,
        session_type=session_type,
        started_at=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id, "started_at": session.started_at.isoformat()}


@router.post("/session/end/{session_id}")
def end_study_session(session_id: int, topics: list = None, db: Session = Depends(get_db)):
    """End a study session."""
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.ended_at = datetime.utcnow()
    session.duration_minutes = int((session.ended_at - session.started_at).total_seconds() / 60)
    if topics:
        session.topics_covered = topics

    # Update progress for covered topics
    for topic_name in (topics or []):
        progress = db.query(Progress).filter(
            Progress.course_id == session.course_id,
            Progress.topic == topic_name
        ).first()
        if not progress:
            progress = Progress(course_id=session.course_id, topic=topic_name)
            db.add(progress)
        progress.times_studied += 1
        progress.last_studied = datetime.utcnow()
        progress.confidence = min(1.0, progress.confidence + 0.1)

    db.commit()
    return {
        "session_id": session.id,
        "duration_minutes": session.duration_minutes,
        "topics_covered": session.topics_covered
    }
