import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, Float, Boolean, DateTime,
    ForeignKey, JSON, Enum as SQLEnum
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.database.session import Base
import enum


class UserRole(str, enum.Enum):
    STUDENT = "student"
    ADMIN = "admin"


class TopicStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVISION = "revision"


class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


# ─── USER MODEL ──────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    courses = relationship("Course", back_populates="user", cascade="all, delete-orphan")
    progress_records = relationship("UserProgress", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")


# ─── COURSE MODEL ─────────────────────────────────────────────────────────────

class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="courses")
    documents = relationship("Document", back_populates="course", cascade="all, delete-orphan")
    units = relationship("Unit", back_populates="course", cascade="all, delete-orphan")
    roadmap = relationship("Roadmap", back_populates="course", uselist=False, cascade="all, delete-orphan")


# ─── DOCUMENT MODEL ───────────────────────────────────────────────────────────

class DocumentType(str, enum.Enum):
    SYLLABUS = "syllabus"
    NOTES = "notes"
    PYQ = "pyq"
    OTHER = "other"


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50))  # pdf, docx, image, etc.
    doc_type = Column(SQLEnum(DocumentType), nullable=False)
    extracted_text = Column(Text)
    metadata = Column(JSON)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="documents")


# ─── KNOWLEDGE GRAPH MODELS ────────────────────────────────────────────────────

class Unit(Base):
    __tablename__ = "units"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    order_index = Column(Integer, default=0)
    importance_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="units")
    topics = relationship("Topic", back_populates="unit", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    unit_id = Column(UUID(as_uuid=True), ForeignKey("units.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    content = Column(Text)  # Teaching content generated
    order_index = Column(Integer, default=0)
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    importance_score = Column(Float, default=0.0)
    pyq_frequency = Column(Integer, default=0)
    estimated_minutes = Column(Integer, default=30)
    prerequisites = Column(ARRAY(UUID(as_uuid=True)), default=[])
    key_points = Column(JSON)  # List of key points
    examples = Column(JSON)  # List of examples
    memory_tricks = Column(JSON)  # Mnemonics
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    unit = relationship("Unit", back_populates="topics")
    subtopics = relationship("Subtopic", back_populates="topic", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="topic", cascade="all, delete-orphan")


class Subtopic(Base):
    __tablename__ = "subtopics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text)
    order_index = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="subtopics")


# ─── ROADMAP MODEL ─────────────────────────────────────────────────────────────

class Roadmap(Base):
    __tablename__ = "roadmaps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False, unique=True)
    structure = Column(JSON)  # Full roadmap tree structure
    total_topics = Column(Integer, default=0)
    estimated_hours = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    course = relationship("Course", back_populates="roadmap")


# ─── PROGRESS TRACKING ─────────────────────────────────────────────────────────

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False)
    status = Column(SQLEnum(TopicStatus), default=TopicStatus.NOT_STARTED)
    score = Column(Float, default=0.0)
    time_spent_minutes = Column(Integer, default=0)
    attempts = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    weak_areas = Column(JSON)  # Identified weak points
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="progress_records")
    topic = relationship("Topic")


# ─── QUIZ MODELS ──────────────────────────────────────────────────────────────

class QuestionType(str, enum.Enum):
    MCQ = "mcq"
    SHORT_ANSWER = "short_answer"
    CONCEPTUAL = "conceptual"


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=False)
    title = Column(String(500))
    difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.INTERMEDIATE)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    topic = relationship("Topic", back_populates="quizzes")
    questions = relationship("Question", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("QuizAttempt", back_populates="quiz", cascade="all, delete-orphan")


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    question_text = Column(Text, nullable=False)
    options = Column(JSON)  # For MCQ: list of options
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text)
    points = Column(Integer, default=1)
    order_index = Column(Integer, default=0)

    # Relationships
    quiz = relationship("Quiz", back_populates="questions")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    quiz_id = Column(UUID(as_uuid=True), ForeignKey("quizzes.id"), nullable=False)
    answers = Column(JSON)  # {question_id: user_answer}
    score = Column(Float, default=0.0)
    max_score = Column(Float, default=0.0)
    percentage = Column(Float, default=0.0)
    time_taken_seconds = Column(Integer)
    feedback = Column(JSON)  # Per-question feedback
    weak_areas = Column(JSON)
    completed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="attempts")


# ─── CHAT / DOUBTS MODEL ──────────────────────────────────────────────────────

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True)
    role = Column(String(20), nullable=False)  # "user" or "assistant"
    content = Column(Text, nullable=False)
    context_used = Column(JSON)  # What context was retrieved
    created_at = Column(DateTime, default=datetime.utcnow)


# ─── ADAPTIVE LEARNING STATE ─────────────────────────────────────────────────

class LearningState(Base):
    __tablename__ = "learning_states"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    current_topic_id = Column(UUID(as_uuid=True), ForeignKey("topics.id"), nullable=True)
    current_difficulty = Column(SQLEnum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    overall_score = Column(Float, default=0.0)
    topics_completed = Column(Integer, default=0)
    topics_total = Column(Integer, default=0)
    weak_topics = Column(JSON, default=[])
    strong_topics = Column(JSON, default=[])
    recommended_next = Column(JSON)  # Next topic suggestions
    revision_queue = Column(JSON, default=[])
    state_data = Column(JSON)  # Additional state machine data
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
