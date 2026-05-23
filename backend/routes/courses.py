"""Course management routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database.connection import get_db
from backend.database.models import Course, Document, Quiz, Progress
from backend.models.schemas import CourseCreate, CourseResponse, CourseUpdate

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=CourseResponse)
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """Create a new course."""
    db_course = Course(
        user_id=1,  # Default user for local-first
        title=course.title,
        semester=course.semester,
        university=course.university,
        subject=course.subject,
        exam_date=course.exam_date,
        color=course.color,
        icon=course.icon
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)

    return _course_to_response(db_course, db)


@router.get("", response_model=List[CourseResponse])
def get_courses(include_archived: bool = False, db: Session = Depends(get_db)):
    """Get all courses."""
    query = db.query(Course).filter(Course.user_id == 1)
    if not include_archived:
        query = query.filter(Course.is_archived == False)
    courses = query.order_by(Course.updated_at.desc()).all()

    return [_course_to_response(c, db) for c in courses]


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get a specific course."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return _course_to_response(course, db)


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, update: CourseUpdate, db: Session = Depends(get_db)):
    """Update a course."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    update_data = update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(course, key, value)

    db.commit()
    db.refresh(course)
    return _course_to_response(course, db)


@router.delete("/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course and all associated data."""
    from backend.rag.vector_store import vector_store

    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Delete vector store collection
    vector_store.delete_collection(course_id)

    db.delete(course)
    db.commit()
    return {"message": "Course deleted successfully"}


def _course_to_response(course: Course, db: Session) -> CourseResponse:
    """Convert course model to response with computed fields."""
    doc_count = db.query(Document).filter(Document.course_id == course.id).count()
    quiz_count = db.query(Quiz).filter(Quiz.course_id == course.id).count()

    # Calculate progress
    progress_records = db.query(Progress).filter(Progress.course_id == course.id).all()
    if progress_records:
        avg_confidence = sum(p.confidence for p in progress_records) / len(progress_records)
        progress_pct = avg_confidence * 100
    else:
        progress_pct = 0.0

    return CourseResponse(
        id=course.id,
        title=course.title,
        semester=course.semester,
        university=course.university,
        subject=course.subject,
        exam_date=course.exam_date,
        color=course.color,
        icon=course.icon,
        is_archived=course.is_archived,
        created_at=course.created_at,
        document_count=doc_count,
        quiz_count=quiz_count,
        progress_percentage=round(progress_pct, 1)
    )
