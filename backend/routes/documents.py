"""Document upload and processing routes."""
import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from backend.database.connection import get_db
from backend.database.models import Document, Course
from backend.models.schemas import DocumentResponse
from backend.parsers.document_parser import DocumentParser, TextChunker
from backend.rag.vector_store import vector_store
from backend.config import UPLOADS_DIR, MAX_FILE_SIZE, ALLOWED_EXTENSIONS

router = APIRouter(prefix="/documents", tags=["documents"])
parser = DocumentParser()
chunker = TextChunker()
ALLOWED_DOCUMENT_TAGS = {
    "syllabus",
    "notes",
    "previous_year_question_paper",
    "assignment",
    "reference_book",
    "lab_manual",
    "other",
}


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    course_id: int = Form(...),
    document_tag: str = Form("notes"),
    db: Session = Depends(get_db)
):
    """Upload and process a document."""
    if document_tag not in ALLOWED_DOCUMENT_TAGS:
        raise HTTPException(status_code=400, detail="Invalid document tag")

    # Validate course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    # Validate file size
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    # Save file
    course_upload_dir = os.path.join(str(UPLOADS_DIR), str(course_id))
    os.makedirs(course_upload_dir, exist_ok=True)
    file_path = os.path.join(course_upload_dir, file.filename)

    with open(file_path, "wb") as f:
        f.write(content)

    # Create document record
    doc = Document(
        course_id=course_id,
        filename=file.filename,
        file_type=ext.lstrip('.'),
        file_path=file_path,
        file_size=len(content),
        is_processed=False,
        extra_metadata={"document_tag": document_tag},
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # Process in background
    background_tasks.add_task(process_document, doc.id, file_path, course_id, document_tag)

    return {
        "id": doc.id,
        "filename": doc.filename,
        "document_tag": document_tag,
        "status": "processing",
        "message": "Document uploaded and queued for processing"
    }


@router.get("/{course_id}", response_model=List[DocumentResponse])
def get_documents(course_id: int, db: Session = Depends(get_db)):
    """Get all documents for a course."""
    docs = db.query(Document).filter(Document.course_id == course_id).all()
    return docs


@router.get("/{course_id}/{doc_id}")
def get_document_status(course_id: int, doc_id: int, db: Session = Depends(get_db)):
    """Get document processing status."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.course_id == course_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": doc.id,
        "filename": doc.filename,
        "is_processed": doc.is_processed,
        "chunk_count": doc.chunk_count
    }


@router.delete("/{course_id}/{doc_id}")
def delete_document(course_id: int, doc_id: int, db: Session = Depends(get_db)):
    """Delete a document and its vectors."""
    doc = db.query(Document).filter(Document.id == doc_id, Document.course_id == course_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    # Delete vectors
    vector_store.delete_document(course_id, doc_id)

    # Delete file
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)

    db.delete(doc)
    db.commit()

    return {"message": "Document deleted successfully"}


def process_document(doc_id: int, file_path: str, course_id: int, document_tag: str):
    """Background task to process uploaded document."""
    from backend.database.connection import get_db_session

    try:
        # Parse document
        result = parser.parse(file_path)
        text = result.get("text", "")

        if not text:
            return

        # Chunk text
        chunks = chunker.chunk(text, metadata={
            "document_id": doc_id,
            "filename": os.path.basename(file_path),
            "document_tag": document_tag,
        })

        # Add to vector store
        if chunks:
            vector_store.add_documents(course_id, chunks, doc_id)

        # Update document record
        with get_db_session() as db:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                doc.is_processed = True
                doc.chunk_count = len(chunks)
                existing_metadata = doc.extra_metadata or {}
                doc.extra_metadata = {
                    **existing_metadata,
                    "document_tag": document_tag,
                    "type": result.get("type"),
                    "text_length": len(text),
                    "page_count": result.get("page_count", 0),
                    "slide_count": result.get("slide_count", 0)
                }

    except Exception as e:
        print(f"Error processing document {doc_id}: {e}")
        with get_db_session() as db:
            doc = db.query(Document).filter(Document.id == doc_id).first()
            if doc:
                existing_metadata = doc.extra_metadata or {}
                doc.extra_metadata = {**existing_metadata, "document_tag": document_tag, "error": str(e)}
