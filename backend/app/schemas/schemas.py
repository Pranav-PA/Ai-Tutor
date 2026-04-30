from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from app.models.models import (
    UserRole, DocumentType, TopicStatus,
    DifficultyLevel, QuestionType
)


# ─── AUTH SCHEMAS ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None


# ─── COURSE SCHEMAS ───────────────────────────────────────────────────────────

class CourseCreate(BaseModel):
    title: str = Field(..., min_length=3)
    description: Optional[str] = None


class CourseResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── DOCUMENT SCHEMAS ─────────────────────────────────────────────────────────

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_type: Optional[str]
    doc_type: DocumentType
    processed: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ─── TOPIC SCHEMAS ────────────────────────────────────────────────────────────

class SubtopicResponse(BaseModel):
    id: UUID
    title: str
    content: Optional[str]
    order_index: int

    class Config:
        from_attributes = True


class TopicResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    content: Optional[str]
    difficulty: DifficultyLevel
    importance_score: float
    pyq_frequency: int
    estimated_minutes: int
    key_points: Optional[Any]
    examples: Optional[Any]
    memory_tricks: Optional[Any]
    order_index: int
    subtopics: List[SubtopicResponse] = []

    class Config:
        from_attributes = True


class UnitResponse(BaseModel):
    id: UUID
    title: str
    description: Optional[str]
    order_index: int
    importance_score: float
    topics: List[TopicResponse] = []

    class Config:
        from_attributes = True


# ─── ROADMAP SCHEMAS ──────────────────────────────────────────────────────────

class RoadmapResponse(BaseModel):
    id: UUID
    course_id: UUID
    structure: Optional[Any]
    total_topics: int
    estimated_hours: float
    created_at: datetime

    class Config:
        from_attributes = True


# ─── PROGRESS SCHEMAS ─────────────────────────────────────────────────────────

class ProgressUpdate(BaseModel):
    status: Optional[TopicStatus] = None
    score: Optional[float] = None
    time_spent_minutes: Optional[int] = None


class ProgressResponse(BaseModel):
    id: UUID
    topic_id: UUID
    status: TopicStatus
    score: float
    time_spent_minutes: int
    attempts: int
    weak_areas: Optional[Any]
    last_accessed: datetime

    class Config:
        from_attributes = True


# ─── QUIZ SCHEMAS ─────────────────────────────────────────────────────────────

class QuizGenerateRequest(BaseModel):
    topic_id: UUID
    num_questions: int = Field(default=5, ge=1, le=20)
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    question_types: List[QuestionType] = [QuestionType.MCQ, QuestionType.SHORT_ANSWER]


class QuestionResponse(BaseModel):
    id: UUID
    question_type: QuestionType
    question_text: str
    options: Optional[Any]
    points: int
    order_index: int

    class Config:
        from_attributes = True


class QuizResponse(BaseModel):
    id: UUID
    topic_id: UUID
    title: Optional[str]
    difficulty: DifficultyLevel
    questions: List[QuestionResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


class AnswerSubmission(BaseModel):
    question_id: UUID
    answer: str


class QuizSubmission(BaseModel):
    quiz_id: UUID
    answers: List[AnswerSubmission]
    time_taken_seconds: Optional[int] = None


class QuizResultResponse(BaseModel):
    id: UUID
    quiz_id: UUID
    score: float
    max_score: float
    percentage: float
    feedback: Optional[Any]
    weak_areas: Optional[Any]
    completed_at: datetime

    class Config:
        from_attributes = True


# ─── CHAT / DOUBT SCHEMAS ─────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    topic_id: Optional[UUID] = None


class ChatResponse(BaseModel):
    role: str
    content: str
    context_used: Optional[Any] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ─── LEARNING STATE SCHEMAS ───────────────────────────────────────────────────

class LearningStateResponse(BaseModel):
    current_topic_id: Optional[UUID]
    current_difficulty: DifficultyLevel
    overall_score: float
    topics_completed: int
    topics_total: int
    weak_topics: Optional[Any]
    strong_topics: Optional[Any]
    recommended_next: Optional[Any]
    revision_queue: Optional[Any]

    class Config:
        from_attributes = True


# ─── ADAPTIVE SCHEMAS ─────────────────────────────────────────────────────────

class AdaptiveRecommendation(BaseModel):
    action: str  # "continue", "revise", "level_up", "level_down"
    next_topic_id: Optional[UUID] = None
    revision_topics: List[UUID] = []
    difficulty_adjustment: Optional[DifficultyLevel] = None
    reasoning: str = ""


# ─── ANALYTICS SCHEMAS ────────────────────────────────────────────────────────

class AnalyticsResponse(BaseModel):
    total_topics: int
    completed_topics: int
    average_score: float
    total_time_spent: int
    weak_areas: List[str]
    strong_areas: List[str]
    score_history: List[Any]
    topic_performance: List[Any]
