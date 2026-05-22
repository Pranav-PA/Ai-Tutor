"""SQLAlchemy database models for AI Semester Companion."""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    learning_style = Column(String(50), default="balanced")  # visual, reading, kinesthetic, balanced
    preferred_provider = Column(String(20), default="openai")  # openai, gemini
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    courses = relationship("Course", back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    semester = Column(String(50))
    university = Column(String(200))
    subject = Column(String(200))
    exam_date = Column(DateTime, nullable=True)
    color = Column(String(7), default="#6366f1")
    icon = Column(String(50), default="book")
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="courses")
    documents = relationship("Document", back_populates="course", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course", cascade="all, delete-orphan")
    flashcards = relationship("Flashcard", back_populates="course", cascade="all, delete-orphan")
    progress = relationship("Progress", back_populates="course", cascade="all, delete-orphan")
    revision_logs = relationship("RevisionLog", back_populates="course", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="course", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    filename = Column(String(500), nullable=False)
    file_type = Column(String(20), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_size = Column(Integer, default=0)
    chunk_count = Column(Integer, default=0)
    is_processed = Column(Boolean, default=False)
    extra_metadata = Column(JSON, default=dict)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="documents")

    @property
    def document_tag(self):
        if not self.extra_metadata:
            return None
        return self.extra_metadata.get("document_tag")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    mode = Column(String(30), default="explain")  # explain, summarize, quiz, revise
    extra_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="chat_history")


class Quiz(Base):
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    quiz_type = Column(String(30), default="mcq")  # mcq, short_answer, coding, numerical
    difficulty = Column(String(20), default="medium")  # easy, medium, hard
    questions = Column(JSON, nullable=False)
    score = Column(Float, nullable=True)
    total_marks = Column(Integer, default=0)
    time_limit = Column(Integer, default=600)  # seconds
    is_completed = Column(Boolean, default=False)
    answers = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    course = relationship("Course", back_populates="quizzes")


class Flashcard(Base):
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    topic = Column(String(200))
    difficulty = Column(String(20), default="medium")
    review_interval = Column(Integer, default=1)  # days
    next_review = Column(DateTime, nullable=True)
    ease_factor = Column(Float, default=2.5)
    repetitions = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="flashcards")


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    topic = Column(String(200), nullable=False)
    unit = Column(String(100))
    confidence = Column(Float, default=0.0)  # 0-1
    times_studied = Column(Integer, default=0)
    times_quizzed = Column(Integer, default=0)
    quiz_accuracy = Column(Float, default=0.0)
    is_weak = Column(Boolean, default=False)
    last_studied = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    course = relationship("Course", back_populates="progress")


class RevisionLog(Base):
    __tablename__ = "revision_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    topic = Column(String(200), nullable=False)
    revision_type = Column(String(30))  # cheat_sheet, flashcard, quick_notes, formula_sheet
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="revision_logs")


class StudySession(Base):
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    duration_minutes = Column(Integer, default=0)
    topics_covered = Column(JSON, default=list)
    session_type = Column(String(30))  # learning, revision, quiz, practice
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    course = relationship("Course", back_populates="study_sessions")
