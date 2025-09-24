import os
import uuid
from pathlib import Path
from typing import Dict, Any, Tuple

from fastapi import HTTPException, status


class FileProcessor:
 
    ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}
    MAX_FILE_SIZE = 50 * 1024 * 1024  
    @classmethod
    def validate_file(cls, filename: str, file_size: int) -> str:
        if not filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file provided"
            )

        file_extension = Path(filename).suffix.lower()

        if file_extension not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed types: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )

        if file_size > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size: 50MB"
            )

        return file_extension

    @classmethod
    def generate_unique_filename(cls, original_filename: str) -> Tuple[str, Path]:
        file_id = str(uuid.uuid4())
        sanitized_filename = f"{file_id}_{original_filename}"
        upload_dir = Path("uploads/documents")
        upload_dir.mkdir(parents=True, exist_ok=True)

        return sanitized_filename, upload_dir / sanitized_filename

    @classmethod
    def save_file(cls, file_path: Path, content: bytes) -> None:
        try:
            with open(file_path, "wb") as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving file: {str(e)}"
            )

    @classmethod
    def extract_text_content(cls, file_path: Path, file_extension: str) -> str:
        try:
            if file_extension == ".pdf":
                return cls._extract_pdf_text(file_path)
            elif file_extension in {".docx", ".doc"}:
                return cls._extract_docx_text(file_path)
            elif file_extension == ".txt":
                return cls._extract_txt_text(file_path)
            else:
                return "Unsupported file type for text extraction."
        except Exception as e:
            return f"Error extracting content: {str(e)}"

    @classmethod
    def _extract_pdf_text(cls, file_path: Path) -> str:
        import pdfplumber
        content = ""

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    content += text + "\n"

        return content.strip() or "No text content could be extracted from this PDF."

    @classmethod
    def _extract_docx_text(cls, file_path: Path) -> str:
        from docx import Document
        content = ""

        doc = Document(file_path)
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                content += paragraph.text + "\n"

        return content.strip() or "No text content could be extracted from this document."

    @classmethod
    def _extract_txt_text(cls, file_path: Path) -> str:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        except UnicodeDecodeError:
            # Fallback to other encodings
            try:
                with open(file_path, "r", encoding="latin-1") as f:
                    return f.read().strip()
            except Exception:
                return "Could not decode text file content."

    @classmethod
    def analyze_content(cls, content: str) -> Dict[str, Any]:
        if not content:
            return {
                "word_count": 0,
                "difficulty_level": "easy"
            }

        # Calculate word count
        word_count = len(content.split())

        # Determine difficulty level
        difficulty_level = "easy" if word_count < 500 else "medium" if word_count < 2000 else "hard"

        return {
            "word_count": word_count,
            "difficulty_level": difficulty_level
        }

    @classmethod
    def cleanup_file(cls, file_path: Path) -> None:
        try:
            if file_path.exists():
                file_path.unlink()
        except Exception:
            pass  # Ignore cleanup errors


def process_uploaded_file(filename: str, file_size: int, content: bytes) -> Dict[str, Any]: 
    # validate file
    file_extension = FileProcessor.validate_file(filename, file_size)

    # create name cho file
    sanitized_filename, file_path = FileProcessor.generate_unique_filename(filename)

    # lưu file
    FileProcessor.save_file(file_path, content)

    # extract nội dung văn bản
    extracted_content = FileProcessor.extract_text_content(file_path, file_extension)

    # phân tích nội dung
    analysis = FileProcessor.analyze_content(extracted_content)

    return {
        "filename": sanitized_filename,
        "file_path": file_path,
        "file_extension": file_extension,
        "extracted_content": extracted_content,
        **analysis
    }
