"""PDF loading utilities for the Multi-Document Chatbot."""

import os
import tempfile
from typing import Dict, List

try:  # pypdf is the modern package name.
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError
except ImportError:  # Backward compatibility for environments using PyPDF2.
    from PyPDF2 import PdfReader
    from PyPDF2.errors import PdfReadError


def load_pdf_pages(file_path: str) -> List[str]:
    """Return a list of extracted page texts from a PDF path.

    Invalid PDF files return an empty list instead of crashing. This keeps
    Streamlit uploads and unit tests stable.
    """
    pages: List[str] = []

    try:
        with open(file_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text.strip())
    except (PdfReadError, OSError, ValueError):
        return []

    return pages


def load_pdf(file_path: str) -> str:
    """Extract text from a PDF file path and preserve page markers."""
    pages = load_pdf_pages(file_path)
    if not pages:
        return ""

    marked_pages = []
    for page_number, page_text in enumerate(pages, start=1):
        if page_text:
            marked_pages.append(f"[PAGE {page_number}]\n{page_text}")

    return "\n\n".join(marked_pages)


def load_pdf_from_upload(uploaded_file) -> str:
    """Extract text from a Streamlit uploaded file object."""
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        return load_pdf(tmp_path)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def load_multiple_pdfs(uploaded_files) -> Dict[str, str]:
    """Load multiple uploaded PDF files and return {filename: extracted_text}."""
    pdf_texts: Dict[str, str] = {}

    for file in uploaded_files:
        pdf_texts[file.name] = load_pdf_from_upload(file)

    return pdf_texts


def get_document_stats(documents: Dict[str, str]) -> dict:
    """Calculate simple document statistics for the Streamlit dashboard."""
    total_pages = 0
    total_words = 0

    for text in documents.values():
        total_pages += text.count("[PAGE ")
        total_words += len(text.split())

    return {
        "documents": len(documents),
        "pages": total_pages,
        "words": total_words,
    }
