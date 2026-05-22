"""Pydantic schemas for request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ---- User Schemas ----
class UserCreate(BaseModel):
    name: str
    learning_style: str = "balanced"
    preferred_provider: str = "openai"


class UserResponse(BaseModel):
    id: int
    name: str
    learning_style: str
    preferred_provider: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    learning_style: Optional[str] = None
    preferred_provider: Optional[str] = None


# ---- Course Schemas ----
class CourseCreate(BaseModel):
    title: str
    semester: Optional[str] = None
    university: Optional[str] = None
    subject: Optional[str] = None
    exam_date: Optional[datetime] = None
    color: str = "#6366f1"
    icon: str = "book"


class CourseResponse(BaseModel):
    id: int
    title: str
    semester: Optional[str]
    university: Optional[str]
    subject: Optional[str]
    exam_date: Optional[datetime]
    color: str
    icon: str
    is_archived: bool
    created_at: datetime
    document_count: int = 0
    quiz_count: int = 0
    progress_percentage: float = 0.0

    class Config:
        from_attributes = True


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    semester: Optional[str] = None
    university: Optional[str] = None
    subject: Optional[str] = None
    exam_date: Optional[datetime] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_archived: Optional[bool] = None


# ---- Document Schemas ----
class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    is_processed: bool
    document_tag: Optional[str] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ---- Chat Schemas ----
class ChatMessage(BaseModel):
    content: str
    mode: str = "explain"  # explain, summarize, quiz, revise
    course_id: int


class ChatResponse(BaseModel):
    id: int
    role: str
    content: str
    mode: str
    metadata: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Quiz Schemas ----
class QuizGenerate(BaseModel):
    course_id: int
    topic: Optional[str] = None
    quiz_type: str = "mcq"  # mcq, short_answer, coding, numerical
    difficulty: str = "medium"  # easy, medium, hard
    num_questions: int = 5


class QuizQuestion(BaseModel):
    question: str
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: str
    marks: int = 1


class QuizResponse(BaseModel):
    id: int
    title: str
    quiz_type: str
    difficulty: str
    questions: List[Dict[str, Any]]
    score: Optional[float]
    total_marks: int
    time_limit: int
    is_completed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class QuizSubmit(BaseModel):
    quiz_id: int
    answers: Dict[str, str]


# ---- Flashcard Schemas ----
class FlashcardCreate(BaseModel):
    course_id: int
    topic: Optional[str] = None
    num_cards: int = 10


class FlashcardResponse(BaseModel):
    id: int
    question: str
    answer: str
    topic: Optional[str]
    difficulty: str
    review_interval: int
    next_review: Optional[datetime]
    repetitions: int

    class Config:
        from_attributes = True


class FlashcardReview(BaseModel):
    flashcard_id: int
    quality: int = Field(ge=0, le=5)  # 0=failed, 5=perfect


# ---- Progress Schemas ----
class ProgressResponse(BaseModel):
    id: int
    topic: str
    unit: Optional[str]
    confidence: float
    times_studied: int
    times_quizzed: int
    quiz_accuracy: float
    is_weak: bool
    last_studied: Optional[datetime]

    class Config:
        from_attributes = True


# ---- Analytics Schemas ----
class AnalyticsResponse(BaseModel):
    syllabus_completion: float
    quiz_accuracy: float
    weak_topics: List[str]
    strong_topics: List[str]
    total_study_hours: float
    revision_streak: int
    ai_readiness_score: float
    topics_by_confidence: List[Dict[str, Any]]
    quiz_history: List[Dict[str, Any]]
    study_sessions: List[Dict[str, Any]]


# ---- Revision Schemas ----
class RevisionRequest(BaseModel):
    course_id: int
    revision_type: str = "cheat_sheet"  # cheat_sheet, formula_sheet, quick_notes, exam_summary
    topic: Optional[str] = None


class RevisionResponse(BaseModel):
    id: int
    topic: str
    revision_type: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---- Study Planner Schemas ----
class StudyPlanRequest(BaseModel):
    course_id: int
    hours_per_day: float = 3.0
    exam_date: Optional[datetime] = None


class StudyPlanResponse(BaseModel):
    course_id: int
    schedule: List[Dict[str, Any]]
    revision_dates: List[str]
    mock_test_dates: List[str]


# ---- Settings Schemas ----
class SettingsUpdate(BaseModel):
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    preferred_provider: Optional[str] = None
    theme: Optional[str] = None


class SettingsResponse(BaseModel):
    has_openai_key: bool
    has_gemini_key: bool
    preferred_provider: str
    theme: str
