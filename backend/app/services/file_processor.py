"""File processing service for document ingestion."""
import os
from typing import Optional
from pathlib import Path

from app.core.config import get_settings

settings = get_settings()


class FileProcessor:
    """Handles file parsing and text extraction."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".png", ".jpg", ".jpeg"}

    def __init__(self):
        os.makedirs(settings.upload_dir, exist_ok=True)

    async def extract_text(self, file_path: str) -> str:
        """Extract text from a file based on its type."""
        ext = Path(file_path).suffix.lower()

        if ext == ".pdf":
            return await self._extract_from_pdf(file_path)
        elif ext in (".docx", ".doc"):
            return await self._extract_from_docx(file_path)
        elif ext == ".txt":
            return await self._extract_from_txt(file_path)
        elif ext in (".png", ".jpg", ".jpeg"):
            return await self._extract_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    async def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF."""
        from PyPDF2 import PdfReader

        reader = PdfReader(file_path)
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        text = "\n\n".join(text_parts)

        # If very little text extracted, try OCR
        if len(text.strip()) < 100:
            text = await self._ocr_pdf(file_path)

        return text

    async def _extract_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX."""
        from docx import Document

        doc = Document(file_path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    async def _extract_from_txt(self, file_path: str) -> str:
        """Extract text from TXT."""
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    async def _extract_from_image(self, file_path: str) -> str:
        """Extract text from image using OCR."""
        try:
            import pytesseract
            from PIL import Image

            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"[OCR Error: {str(e)}]"

    async def _ocr_pdf(self, file_path: str) -> str:
        """OCR a PDF file by converting pages to images."""
        try:
            import pytesseract
            from PIL import Image
            from PyPDF2 import PdfReader
            import io

            # Simplified: just extract what we can
            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                if "/XObject" in (page.get("/Resources") or {}):
                    x_objects = page["/Resources"]["/XObject"].get_object()
                    for obj_name in x_objects:
                        obj = x_objects[obj_name].get_object()
                        if obj["/Subtype"] == "/Image":
                            # Extract image and OCR
                            data = obj.get_data()
                            img = Image.open(io.BytesIO(data))
                            text_parts.append(pytesseract.image_to_string(img))

            return "\n\n".join(text_parts) if text_parts else "[No text extracted]"
        except Exception:
            return "[OCR processing failed]"

    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
        """Split text into overlapping chunks for embedding."""
        if not text:
            return []

        chunks = []
        sentences = text.replace("\n\n", "\n").split("\n")
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) > chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                # Keep overlap
                words = current_chunk.split()
                overlap_text = " ".join(words[-overlap // 5:]) if words else ""
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk += "\n" + sentence

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks


# Singleton
file_processor = FileProcessor()
