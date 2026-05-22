"""Ingestion Agent - Handles file uploads, OCR, and text extraction."""
import os
import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.agents.base import BaseAgent, AgentContext, AgentResult
from app.services import file_processor, vector_store
from app.models import Document, DocumentType
from app.core.config import get_settings

settings = get_settings()


class IngestionAgent(BaseAgent):
    """
    Handles file uploads, OCR + parsing, and structures text.
    
    Responsibilities:
    - Accept uploaded files (PDF, DOCX, images, text)
    - Extract text using appropriate parser (PyPDF2, python-docx, pytesseract)
    - Clean and normalize extracted text
    - Chunk text for embedding
    - Store embeddings in vector store
    """

    def __init__(self):
        super().__init__(
            name="ingestion_agent",
            description="Processes uploaded documents and extracts structured text"
        )

    async def execute(self, context: AgentContext) -> AgentResult:
        """Process uploaded documents."""
        db: AsyncSession = context.get("db")
        course_id = context.course_id
        file_paths: List[str] = context.get("file_paths", [])
        doc_types: List[str] = context.get("doc_types", [])

        if not file_paths:
            return AgentResult(success=False, error="No files provided")

        processed_docs = []
        all_chunks = []
        all_metadata = []

        for i, file_path in enumerate(file_paths):
            doc_type = doc_types[i] if i < len(doc_types) else "other"

            try:
                # Extract text
                text = await file_processor.extract_text(file_path)

                if not text or len(text.strip()) < 10:
                    self._logger.warning("empty_extraction", file=file_path)
                    continue

                # Clean text
                cleaned_text = self._clean_text(text)

                # Chunk for embeddings
                chunks = file_processor.chunk_text(cleaned_text)

                # Create metadata for each chunk
                for j, chunk in enumerate(chunks):
                    all_chunks.append(chunk)
                    all_metadata.append({
                        "course_id": course_id,
                        "doc_type": doc_type,
                        "file_path": file_path,
                        "chunk_index": j,
                        "filename": os.path.basename(file_path),
                    })

                processed_docs.append({
                    "file_path": file_path,
                    "doc_type": doc_type,
                    "text_length": len(cleaned_text),
                    "num_chunks": len(chunks),
                    "extracted_text": cleaned_text,
                })

            except Exception as e:
                self._logger.error("file_processing_error", file=file_path, error=str(e))
                continue

        # Store embeddings in vector store
        if all_chunks:
            await vector_store.add_documents(
                course_id=course_id,
                texts=all_chunks,
                metadata=all_metadata,
            )

        return AgentResult(
            success=True,
            data={
                "processed_documents": processed_docs,
                "total_chunks": len(all_chunks),
                "course_id": course_id,
            },
            next_agent="knowledge_extraction_agent"
        )

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        import re

        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        # Remove common artifacts
        text = re.sub(r'\x00', '', text)  # Null bytes
        text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f]', '', text)  # Control chars

        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        return text.strip()
