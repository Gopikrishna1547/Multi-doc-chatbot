import pytest
import os
import tempfile
from unittest.mock import MagicMock
from src.pdf_loader import load_multiple_pdfs, load_pdf
from src.vector_store import split_text, build_vector_store
from src.chat_history import format_chat_history, get_chat_summary, clear_chat_history


class TestPdfLoader:
    """Tests for pdf_loader module."""

    def test_load_multiple_pdfs_returns_dict(self):
        """Test that load_multiple_pdfs returns a dictionary."""
        mock_file = MagicMock()
        mock_file.name = "test.pdf"
        mock_file.read.return_value = b"fake pdf content"
        result = load_multiple_pdfs([mock_file])
        assert isinstance(result, dict)

    def test_load_multiple_pdfs_empty_list(self):
        """Test that empty list returns empty dictionary."""
        result = load_multiple_pdfs([])
        assert result == {}

    def test_load_multiple_pdfs_correct_keys(self):
        """Test that dictionary keys match uploaded file names."""
        mock_file = MagicMock()
        mock_file.name = "document.pdf"
        mock_file.read.return_value = b"fake content"
        result = load_multiple_pdfs([mock_file])
        assert "document.pdf" in result
