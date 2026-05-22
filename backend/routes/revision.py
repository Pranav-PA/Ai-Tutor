"""Revision and flashcard routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from backend.database.connection import get_db
from backend.database.models import Flashcard, RevisionLog, Course, Progress
from backend.models.schemas import (
    FlashcardCreate, FlashcardResponse, FlashcardReview,
    RevisionRequest, RevisionResponse
)
from backend.agents.orchestrator import orchestrator

router = APIRouter(prefix="/revision", tags=["revision"])


@router.post("/generate")
def generate_revision(request: RevisionRequest, db: Session = Depends(get_db)):
    """Generate revision material."""
    course = db.query(Course).filter(Course.id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    content = orchestrator.generate_revision(
        course_id=request.course_id,
        revision_type=request.revision_type,
        topic=request.topic
    )

    # Save revision log
    log = RevisionLog(
        course_id=request.course_id,
        topic=request.topic or "General",
        revision_type=request.revision_type,
        content=content
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return RevisionResponse(
        id=log.id,
        topic=log.topic,
        revision_type=log.revision_type,
        content=log.content,
        created_at=log.created_at
    )


@router.get("/{course_id}", response_model=List[RevisionResponse])
def get_revisions(course_id: int, db: Session = Depends(get_db)):
    """Get all revision logs for a course."""
    logs = db.query(RevisionLog).filter(
        RevisionLog.course_id == course_id
    ).order_by(RevisionLog.created_at.desc()).all()

    return [
        RevisionResponse(
            id=log.id,
            topic=log.topic,
            revision_type=log.revision_type,
            content=log.content,
            created_at=log.created_at
        )
        for log in logs
    ]


# ---- Flashcard Routes ----
@router.post("/flashcards/generate")
def generate_flashcards(request: FlashcardCreate, db: Session = Depends(get_db)):
    """Generate flashcards for a course."""
    course = db.query(Course).filter(Course.id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    result = orchestrator.generate_flashcards(
        course_id=request.course_id,
        topic=request.topic,
        num_cards=request.num_cards
    )

    cards = result.get("flashcards", [])
    saved_cards = []

    for card in cards:
        fc = Flashcard(
            course_id=request.course_id,
            question=card.get("question", ""),
            answer=card.get("answer", ""),
            topic=card.get("topic", request.topic or "General"),
            difficulty=card.get("difficulty", "medium"),
            next_review=datetime.utcnow() + timedelta(days=1)
        )
        db.add(fc)
        saved_cards.append(fc)

    db.commit()

    return {
        "generated": len(saved_cards),
        "flashcards": [
            FlashcardResponse(
                id=fc.id,
                question=fc.question,
                answer=fc.answer,
                topic=fc.topic,
                difficulty=fc.difficulty,
                review_interval=fc.review_interval,
                next_review=fc.next_review,
                repetitions=fc.repetitions
            )
            for fc in saved_cards
        ]
    }


@router.get("/flashcards/{course_id}", response_model=List[FlashcardResponse])
def get_flashcards(course_id: int, due_only: bool = False, db: Session = Depends(get_db)):
    """Get flashcards for a course."""
    query = db.query(Flashcard).filter(Flashcard.course_id == course_id)

    if due_only:
        query = query.filter(Flashcard.next_review <= datetime.utcnow())

    cards = query.order_by(Flashcard.next_review.asc()).all()

    return [
        FlashcardResponse(
            id=fc.id,
            question=fc.question,
            answer=fc.answer,
            topic=fc.topic,
            difficulty=fc.difficulty,
            review_interval=fc.review_interval,
            next_review=fc.next_review,
            repetitions=fc.repetitions
        )
        for fc in cards
    ]


@router.post("/flashcards/review")
def review_flashcard(review: FlashcardReview, db: Session = Depends(get_db)):
    """Review a flashcard using SM-2 spaced repetition algorithm."""
    fc = db.query(Flashcard).filter(Flashcard.id == review.flashcard_id).first()
    if not fc:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    quality = review.quality

    # SM-2 Algorithm
    if quality >= 3:
        if fc.repetitions == 0:
            fc.review_interval = 1
        elif fc.repetitions == 1:
            fc.review_interval = 6
        else:
            fc.review_interval = int(fc.review_interval * fc.ease_factor)
        fc.repetitions += 1
    else:
        fc.repetitions = 0
        fc.review_interval = 1

    # Update ease factor
    fc.ease_factor = max(1.3, fc.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
    fc.next_review = datetime.utcnow() + timedelta(days=fc.review_interval)

    db.commit()

    return {
        "flashcard_id": fc.id,
        "next_review": fc.next_review.isoformat(),
        "review_interval": fc.review_interval,
        "ease_factor": fc.ease_factor
    }


@router.delete("/flashcards/{flashcard_id}")
def delete_flashcard(flashcard_id: int, db: Session = Depends(get_db)):
    """Delete a flashcard."""
    fc = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not fc:
        raise HTTPException(status_code=404, detail="Flashcard not found")

    db.delete(fc)
    db.commit()
    return {"message": "Flashcard deleted"}
