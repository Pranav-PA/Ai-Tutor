"""Quiz routes - Quiz generation, submission, and results."""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.auth.security import get_current_user
from app.models import (
    User, Topic, Unit, Quiz, Question, QuestionType,
    QuizAttempt, UserProgress, DifficultyLevel
)
from app.schemas import (
    QuizGenerateRequest, QuizResponse, QuizSubmission,
    QuizResultResponse, QuestionResponse
)
from app.agents import agent_runtime, AgentContext

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/generate", response_model=QuizResponse)
async def generate_quiz(
    request: QuizGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate a new quiz for a topic."""
    # Get topic
    result = await db.execute(select(Topic).where(Topic.id == request.topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    # Get course_id
    result = await db.execute(select(Unit).where(Unit.id == topic.unit_id))
    unit = result.scalar_one_or_none()

    # Generate quiz using Quiz Agent
    context = AgentContext(
        user_id=str(current_user.id),
        course_id=str(unit.course_id),
        topic_id=str(topic.id),
    )
    context.set("topic_title", topic.title)
    context.set("num_questions", request.num_questions)
    context.set("difficulty", request.difficulty.value)
    context.set("question_types", [qt.value for qt in request.question_types])

    quiz_agent = agent_runtime.get_agent("quiz_agent")
    result_agent = await quiz_agent.run(context)

    if not result_agent.success:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {result_agent.error}")

    generated_questions = result_agent.data.get("questions", [])

    # Create quiz in database
    quiz = Quiz(
        topic_id=topic.id,
        title=f"Quiz: {topic.title}",
        difficulty=request.difficulty,
    )
    db.add(quiz)
    await db.flush()

    # Create questions
    for i, q_data in enumerate(generated_questions):
        question = Question(
            quiz_id=quiz.id,
            question_type=QuestionType(q_data.get("type", "mcq")),
            question_text=q_data["question"],
            options=q_data.get("options"),
            correct_answer=q_data["correct_answer"],
            explanation=q_data.get("explanation", ""),
            points=q_data.get("points", 1),
            order_index=i,
        )
        db.add(question)

    await db.commit()
    await db.refresh(quiz)

    # Load questions for response
    result = await db.execute(
        select(Quiz)
        .where(Quiz.id == quiz.id)
        .options(selectinload(Quiz.questions))
    )
    quiz = result.scalar_one()

    return quiz


@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a quiz by ID (without correct answers)."""
    result = await db.execute(
        select(Quiz)
        .where(Quiz.id == quiz_id)
        .options(selectinload(Quiz.questions))
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


@router.post("/submit", response_model=QuizResultResponse)
async def submit_quiz(
    submission: QuizSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit quiz answers for evaluation."""
    # Get quiz with questions
    result = await db.execute(
        select(Quiz)
        .where(Quiz.id == submission.quiz_id)
        .options(selectinload(Quiz.questions))
    )
    quiz = result.scalar_one_or_none()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # Get topic and course
    result = await db.execute(select(Topic).where(Topic.id == quiz.topic_id))
    topic = result.scalar_one_or_none()
    result = await db.execute(select(Unit).where(Unit.id == topic.unit_id))
    unit = result.scalar_one_or_none()

    # Build answers map
    question_map = {str(q.id): q for q in quiz.questions}
    user_answers = {}
    for answer in submission.answers:
        q_id = str(answer.question_id)
        if q_id in question_map:
            user_answers[str(quiz.questions.index(question_map[q_id]))] = answer.answer

    # Use Evaluation Agent
    context = AgentContext(
        user_id=str(current_user.id),
        course_id=str(unit.course_id),
        topic_id=str(topic.id),
    )
    context.set("questions", [
        {
            "question": q.question_text,
            "correct_answer": q.correct_answer,
            "type": q.question_type.value,
            "points": q.points,
            "options": q.options,
        }
        for q in sorted(quiz.questions, key=lambda x: x.order_index)
    ])
    context.set("user_answers", user_answers)
    context.set("topic_title", topic.title)

    eval_agent = agent_runtime.get_agent("evaluation_agent")
    eval_result = await eval_agent.run(context)

    if not eval_result.success:
        raise HTTPException(status_code=500, detail="Evaluation failed")

    # Create quiz attempt record
    attempt = QuizAttempt(
        user_id=current_user.id,
        quiz_id=quiz.id,
        answers={str(a.question_id): a.answer for a in submission.answers},
        score=eval_result.data.get("total_score", 0),
        max_score=eval_result.data.get("max_score", 0),
        percentage=eval_result.data.get("percentage", 0),
        time_taken_seconds=submission.time_taken_seconds,
        feedback=eval_result.data.get("results", []),
        weak_areas=eval_result.data.get("weak_areas", []),
    )
    db.add(attempt)

    # Update user progress
    result = await db.execute(
        select(UserProgress).where(
            UserProgress.user_id == current_user.id,
            UserProgress.topic_id == topic.id,
        )
    )
    progress = result.scalar_one_or_none()
    if progress:
        progress.score = max(progress.score, eval_result.data.get("percentage", 0))
        progress.weak_areas = eval_result.data.get("weak_areas", [])

    await db.commit()
    await db.refresh(attempt)

    return attempt


@router.get("/attempts/{course_id}")
async def get_quiz_history(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get quiz attempt history for a course."""
    result = await db.execute(
        select(QuizAttempt)
        .join(Quiz)
        .join(Topic)
        .join(Unit)
        .where(
            Unit.course_id == course_id,
            QuizAttempt.user_id == current_user.id,
        )
        .order_by(QuizAttempt.completed_at.desc())
    )
    attempts = result.scalars().all()

    return [
        {
            "id": str(a.id),
            "quiz_id": str(a.quiz_id),
            "score": a.score,
            "max_score": a.max_score,
            "percentage": a.percentage,
            "completed_at": a.completed_at.isoformat(),
            "weak_areas": a.weak_areas,
        }
        for a in attempts
    ]
