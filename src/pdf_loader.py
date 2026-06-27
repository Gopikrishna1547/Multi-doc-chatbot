import tempfile
import os
from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError


def load_pdf(file_path: str) -> str:
    text = ""

    try:
        with open(file_path, "rb") as f:
            reader = PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        return text

    except PdfReadError:
        return ""


def load_pdf_from_upload(uploaded_file) -> str:
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        return load_pdf(tmp_path)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def load_multiple_pdfs(uploaded_files) -> dict:
    pdf_texts = {}

    for file in uploaded_files:
        pdf_texts[file.name] = load_pdf_from_upload(file)

    return pdf_texts
