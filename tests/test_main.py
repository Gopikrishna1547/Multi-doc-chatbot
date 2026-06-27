import pytest
import os
import tempfile
from unittest.mock import MagicMock
from src.pdf_loader import load_multiple_pdfs, load_pdf
from src.vector_store import split_text, build_vector_store
from src.chat_history import format_chat_history, get_chat_summary, clear_chat_history
