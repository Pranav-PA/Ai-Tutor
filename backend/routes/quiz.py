"""Quiz routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from backend.database.connection import get_db
from backend.database.models import Quiz, Course, Progress
from backend.models.schemas import QuizGenerate, QuizResponse, QuizSubmit
from backend.agents.orchestrator import orchestrator

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("/generate", response_model=QuizResponse)
def generate_quiz(request: QuizGenerate, db: Session = Depends(get_db)):
    """Generate a new quiz."""
    # Validate course
    course = db.query(Course).filter(Course.id == request.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Generate quiz using AI
    result = orchestrator.generate_quiz(
        course_id=request.course_id,
        topic=request.topic,
        quiz_type=request.quiz_type,
        difficulty=request.difficulty,
        num_questions=request.num_questions
    )

    if "error" in result:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {result.get('error')}")

    questions = result.get("questions", [])
    total_marks = result.get("total_marks", len(questions))
    title = result.get("title", f"{request.quiz_type.upper()} Quiz - {request.topic or 'General'}")

    # Save quiz
    quiz = Quiz(
        course_id=request.course_id,
        title=title,
        quiz_type=request.quiz_type,
        difficulty=request.difficulty,
        questions=questions,
        total_marks=total_marks,
        time_limit=request.num_questions * 120  # 2 min per question
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)

    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        quiz_type=quiz.quiz_type,
        difficulty=quiz.difficulty,
        questions=quiz.questions,
        score=quiz.score,
        total_marks=quiz.total_marks,
        time_limit=quiz.time_limit,
        is_completed=quiz.is_completed,
        created_at=quiz.created_at
    )


@router.post("/submit")
def submit_quiz(submission: QuizSubmit, db: Session = Depends(get_db)):
    """Submit quiz answers and get results."""
    quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Grade the quiz
    correct = 0
    total = len(quiz.questions)
    results = []

    for i, question in enumerate(quiz.questions):
        q_id = str(i)
        user_answer = submission.answers.get(q_id, "")
        correct_answer = question.get("correct_answer", "")

        is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
        if is_correct:
            correct += 1

        results.append({
            "question_id": i,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question.get("explanation", "")
        })

    score = (correct / total * 100) if total > 0 else 0

    # Update quiz
    quiz.score = score
    quiz.is_completed = True
    quiz.answers = submission.answers
    quiz.completed_at = datetime.utcnow()
    db.commit()

    # Update progress for related topics
    for question in quiz.questions:
        topic = question.get("topic", "General")
        progress = db.query(Progress).filter(
            Progress.course_id == quiz.course_id,
            Progress.topic == topic
        ).first()

        if not progress:
            progress = Progress(
                course_id=quiz.course_id,
                topic=topic,
                times_quizzed=0,
                times_studied=0,
                quiz_accuracy=0.0,
                confidence=0.0,
            )
            db.add(progress)
            db.flush()

        progress.times_quizzed = (progress.times_quizzed or 0) + 1
        # Update accuracy with rolling average
        prev_accuracy = progress.quiz_accuracy or 0.0
        progress.quiz_accuracy = (
            (prev_accuracy * (progress.times_quizzed - 1) + (score / 100))
            / progress.times_quizzed
        )
        progress.confidence = min(1.0, progress.quiz_accuracy * 0.7 + ((progress.times_studied or 0) * 0.1))
        progress.is_weak = progress.quiz_accuracy < 0.5

    db.commit()

    return {
        "quiz_id": quiz.id,
        "score": score,
        "correct": correct,
        "total": total,
        "results": results
    }


@router.get("/{course_id}", response_model=List[QuizResponse])
def get_quizzes(course_id: int, db: Session = Depends(get_db)):
    """Get all quizzes for a course."""
    quizzes = db.query(Quiz).filter(Quiz.course_id == course_id).order_by(Quiz.created_at.desc()).all()
    return [
        QuizResponse(
            id=q.id,
            title=q.title,
            quiz_type=q.quiz_type,
            difficulty=q.difficulty,
            questions=q.questions,
            score=q.score,
            total_marks=q.total_marks,
            time_limit=q.time_limit,
            is_completed=q.is_completed,
            created_at=q.created_at
        )
        for q in quizzes
    ]


@router.get("/single/{quiz_id}", response_model=QuizResponse)
def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    """Get a specific quiz."""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        quiz_type=quiz.quiz_type,
        difficulty=quiz.difficulty,
        questions=quiz.questions,
        score=quiz.score,
        total_marks=quiz.total_marks,
        time_limit=quiz.time_limit,
        is_completed=quiz.is_completed,
        created_at=quiz.created_at
    )
