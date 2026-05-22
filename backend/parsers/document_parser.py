"""Document parsing pipeline - PDF, DOCX, PPTX, images with OCR."""
import os
import re
from typing import List, Dict, Any
from pathlib import Path

import pdfplumber
from docx import Document as DocxDocument
from pptx import Presentation
from PIL import Image
try:
    import pytesseract
    HAS_TESSERACT = True
except Exception:
    HAS_TESSERACT = False


class DocumentParser:
    """Unified document parser supporting multiple formats."""

    def __init__(self):
        self.supported_extensions = {'.pdf', '.docx', '.pptx', '.txt', '.png', '.jpg', '.jpeg'}

    def parse(self, file_path: str) -> Dict[str, Any]:
        """Parse a document and return extracted text with metadata."""
        path = Path(file_path)
        ext = path.suffix.lower()

        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {ext}")

        if ext == '.pdf':
            return self._parse_pdf(file_path)
        elif ext == '.docx':
            return self._parse_docx(file_path)
        elif ext == '.pptx':
            return self._parse_pptx(file_path)
        elif ext == '.txt':
            return self._parse_txt(file_path)
        elif ext in {'.png', '.jpg', '.jpeg'}:
            return self._parse_image(file_path)

    def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse PDF using pdfplumber with OCR fallback."""
        pages = []
        full_text = ""

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""

                # If very little text found, try OCR on page image
                if len(text.strip()) < 50 and HAS_TESSERACT:
                    try:
                        img = page.to_image(resolution=200).original
                        text = pytesseract.image_to_string(img)
                    except Exception:
                        pass

                # Also extract tables
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row:
                            row_text = " | ".join(str(cell) if cell else "" for cell in row)
                            text += "\n" + row_text

                pages.append({
                    "page": page_num + 1,
                    "text": text.strip()
                })
                full_text += text + "\n\n"

        return {
            "text": self._clean_text(full_text),
            "pages": pages,
            "page_count": len(pages),
            "type": "pdf"
        }

    def _parse_docx(self, file_path: str) -> Dict[str, Any]:
        """Parse DOCX document."""
        doc = DocxDocument(file_path)
        paragraphs = []
        full_text = ""

        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())
                full_text += para.text + "\n"

        # Also extract tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells)
                if row_text.strip():
                    full_text += row_text + "\n"

        return {
            "text": self._clean_text(full_text),
            "paragraphs": paragraphs,
            "type": "docx"
        }

    def _parse_pptx(self, file_path: str) -> Dict[str, Any]:
        """Parse PowerPoint presentation."""
        prs = Presentation(file_path)
        slides = []
        full_text = ""

        for slide_num, slide in enumerate(prs.slides):
            slide_text = ""
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_text += shape.text + "\n"

            slides.append({
                "slide": slide_num + 1,
                "text": slide_text.strip()
            })
            full_text += slide_text + "\n\n"

        return {
            "text": self._clean_text(full_text),
            "slides": slides,
            "slide_count": len(slides),
            "type": "pptx"
        }

    def _parse_txt(self, file_path: str) -> Dict[str, Any]:
        """Parse plain text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        return {
            "text": self._clean_text(text),
            "type": "txt"
        }

    def _parse_image(self, file_path: str) -> Dict[str, Any]:
        """Parse image using OCR."""
        try:
            img = Image.open(file_path)
            if HAS_TESSERACT:
                text = pytesseract.image_to_string(img)
            else:
                text = "[OCR not available - install tesseract-ocr]"
        except Exception as e:
            text = f"[OCR failed: {str(e)}]"

        return {
            "text": self._clean_text(text),
            "type": "image"
        }

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        # Remove non-printable characters
        text = re.sub(r'[^\x20-\x7E\n\t]', '', text)
        return text.strip()


class TextChunker:
    """Split text into overlapping chunks for embedding."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into chunks with metadata."""
        if not text:
            return []

        chunks = []
        start = 0
        chunk_id = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for period, question mark, or newline near the end
                break_point = text.rfind('.', start + self.chunk_size - 200, end)
                if break_point == -1:
                    break_point = text.rfind('\n', start + self.chunk_size - 200, end)
                if break_point > start:
                    end = break_point + 1

            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_data = {
                    "id": chunk_id,
                    "text": chunk_text,
                    "start": start,
                    "end": end,
                    "metadata": metadata or {}
                }
                chunks.append(chunk_data)
                chunk_id += 1

            start = end - self.overlap

        return chunks
