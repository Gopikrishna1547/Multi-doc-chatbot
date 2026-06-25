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


def load_multiple_pdfs(files: list) -> dict:
    """Extract text from multiple PDF files and return as dictionary."""
    log.info(f"Loading {len(files)} PDF files")
    documents = {}
    for file in files:
        name = file.name
        text = load_pdf_from_upload(file)
        documents[name] = text
        log.info(f"Loaded: {name}")
    return documents


def load_pdf_from_upload(uploaded_file) -> str:
    """Extract text from a Streamlit uploaded file object."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name
    text = load_pdf(tmp_path)
    os.unlink(tmp_path)
    return text
