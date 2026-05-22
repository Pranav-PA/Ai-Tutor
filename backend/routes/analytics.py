"""Analytics routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from backend.database.connection import get_db
from backend.database.models import Course, Quiz, Progress, StudySession, Flashcard, RevisionLog
from backend.models.schemas import AnalyticsResponse, ProgressResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/{course_id}", response_model=AnalyticsResponse)
def get_analytics(course_id: int, db: Session = Depends(get_db)):
    """Get comprehensive analytics for a course."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Progress data
    progress_records = db.query(Progress).filter(Progress.course_id == course_id).all()

    # Quiz data
    quizzes = db.query(Quiz).filter(
        Quiz.course_id == course_id,
        Quiz.is_completed == True
    ).order_by(Quiz.completed_at.desc()).all()

    # Study sessions
    sessions = db.query(StudySession).filter(StudySession.course_id == course_id).all()

    # Calculate metrics
    topics_confidence = [
        {"topic": p.topic, "confidence": p.confidence, "is_weak": p.is_weak}
        for p in progress_records
    ]

    weak_topics = [p.topic for p in progress_records if p.is_weak]
    strong_topics = [p.topic for p in progress_records if p.confidence >= 0.7]

    # Syllabus completion
    total_topics = len(progress_records) if progress_records else 1
    studied_topics = sum(1 for p in progress_records if p.times_studied > 0)
    syllabus_completion = (studied_topics / total_topics * 100) if total_topics > 0 else 0

    # Quiz accuracy
    quiz_scores = [q.score for q in quizzes if q.score is not None]
    avg_quiz_accuracy = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0

    # Total study hours
    total_minutes = sum(s.duration_minutes for s in sessions)
    total_hours = total_minutes / 60

    # Revision streak
    revision_logs = db.query(RevisionLog).filter(
        RevisionLog.course_id == course_id
    ).order_by(RevisionLog.created_at.desc()).all()
    revision_streak = _calculate_streak(revision_logs)

    # AI readiness score
    readiness = _calculate_readiness(syllabus_completion, avg_quiz_accuracy, len(weak_topics), total_topics)

    # Quiz history for chart
    quiz_history = [
        {
            "date": q.completed_at.isoformat() if q.completed_at else q.created_at.isoformat(),
            "score": q.score,
            "type": q.quiz_type,
            "difficulty": q.difficulty
        }
        for q in quizzes[:20]
    ]

    # Study sessions for chart
    session_data = [
        {
            "date": s.started_at.isoformat(),
            "duration": s.duration_minutes,
            "type": s.session_type
        }
        for s in sessions[:30]
    ]

    return AnalyticsResponse(
        syllabus_completion=round(syllabus_completion, 1),
        quiz_accuracy=round(avg_quiz_accuracy, 1),
        weak_topics=weak_topics,
        strong_topics=strong_topics,
        total_study_hours=round(total_hours, 1),
        revision_streak=revision_streak,
        ai_readiness_score=round(readiness, 1),
        topics_by_confidence=topics_confidence,
        quiz_history=quiz_history,
        study_sessions=session_data
    )


@router.get("/progress/{course_id}", response_model=List[ProgressResponse])
def get_progress(course_id: int, db: Session = Depends(get_db)):
    """Get topic-wise progress for a course."""
    progress = db.query(Progress).filter(Progress.course_id == course_id).all()
    return [
        ProgressResponse(
            id=p.id,
            topic=p.topic,
            unit=p.unit,
            confidence=p.confidence,
            times_studied=p.times_studied,
            times_quizzed=p.times_quizzed,
            quiz_accuracy=p.quiz_accuracy,
            is_weak=p.is_weak,
            last_studied=p.last_studied
        )
        for p in progress
    ]


def _calculate_streak(logs) -> int:
    """Calculate consecutive days of revision."""
    if not logs:
        return 0

    from datetime import datetime, timedelta
    streak = 0
    today = datetime.utcnow().date()
    current_date = today

    dates = set(log.created_at.date() for log in logs)

    while current_date in dates:
        streak += 1
        current_date -= timedelta(days=1)

    return streak


def _calculate_readiness(completion: float, accuracy: float, weak_count: int, total: int) -> float:
    """Calculate AI readiness score (0-100)."""
    completion_score = completion * 0.3
    accuracy_score = accuracy * 0.4
    weakness_penalty = (weak_count / max(total, 1)) * 30
    return max(0, min(100, completion_score + accuracy_score - weakness_penalty))
