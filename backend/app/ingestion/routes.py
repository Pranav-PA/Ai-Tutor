"""Ingestion routes - File upload and processing."""
import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.auth.security import get_current_user
from app.models import User, Course, Document, DocumentType
from app.schemas import CourseCreate, CourseResponse, DocumentResponse
from app.agents import agent_runtime, AgentContext, LearningPhase
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/ingestion", tags=["Ingestion"])


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new course/subject."""
    course = Course(
        user_id=current_user.id,
        title=course_data.title,
        description=course_data.description,
    )
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


@router.get("/courses", response_model=List[CourseResponse])
async def list_courses(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all courses for the current user."""
    result = await db.execute(
        select(Course).where(Course.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/courses/{course_id}/upload", response_model=List[DocumentResponse])
async def upload_documents(
    course_id: str,
    doc_type: str = Form(...),
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload documents (syllabus, notes, PYQs) for a course."""
    # Verify course ownership
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.user_id == current_user.id)
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Validate doc_type
    try:
        dtype = DocumentType(doc_type)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid doc_type. Use: {[e.value for e in DocumentType]}")

    # Process uploads
    upload_dir = os.path.join(settings.upload_dir, str(course_id))
    os.makedirs(upload_dir, exist_ok=True)

    documents = []
    for file in files:
        # Validate file size
        content = await file.read()
        if len(content) > settings.max_upload_size:
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds maximum size")

        # Save file
        file_ext = os.path.splitext(file.filename)[1].lower()
        file_id = str(uuid.uuid4())
        file_path = os.path.join(upload_dir, f"{file_id}{file_ext}")

        with open(file_path, "wb") as f:
            f.write(content)

        # Create document record
        doc = Document(
            course_id=course.id,
            filename=file.filename,
            file_path=file_path,
            file_type=file_ext.lstrip("."),
            doc_type=dtype,
            processed=False,
        )
        db.add(doc)
        documents.append(doc)

    await db.commit()
    for doc in documents:
        await db.refresh(doc)

    return documents


@router.post("/courses/{course_id}/process")
async def process_course(
    course_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Process all uploaded documents and generate the knowledge structure."""
    # Get course and documents
    result = await db.execute(
        select(Course).where(Course.id == course_id, Course.user_id == current_user.id)
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    result = await db.execute(
        select(Document).where(Document.course_id == course.id, Document.processed == False)
    )
    unprocessed_docs = result.scalars().all()

    if not unprocessed_docs:
        raise HTTPException(status_code=400, detail="No unprocessed documents found")

    # Prepare context for agent pipeline
    context = AgentContext(
        user_id=str(current_user.id),
        course_id=str(course_id),
    )
    context.set("db", db)
    context.set("file_paths", [doc.file_path for doc in unprocessed_docs])
    context.set("doc_types", [doc.doc_type.value for doc in unprocessed_docs])

    # Execute the processing pipeline
    pipeline_phases = [
        LearningPhase.INGESTION,
        LearningPhase.KNOWLEDGE_EXTRACTION,
        LearningPhase.WEIGHTAGE_ANALYSIS,
        LearningPhase.ROADMAP_GENERATION,
    ]

    results = await agent_runtime.execute_pipeline(pipeline_phases, context)

    # Mark documents as processed
    for doc in unprocessed_docs:
        doc.processed = True
    await db.commit()

    # Get roadmap data
    roadmap_data = context.get("roadmap_agent.roadmap", {})

    return {
        "status": "success",
        "message": "Course processed successfully",
        "roadmap": roadmap_data,
        "pipeline_results": {
            phase: {"success": r.success, "error": r.error}
            for phase, r in results.items()
        },
    }
