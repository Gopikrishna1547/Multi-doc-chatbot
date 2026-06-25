import logging
from pypdf import PdfReader

log = logging.getLogger(__name__)


def load_pdf(filepath: str) -> str:
    """Extract all text from a single PDF file."""
    log.info(f"Loading PDF: {filepath}")
    reader = PdfReader(filepath)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    log.info(f"Extracted text from {len(reader.pages)} pages")
    return text
