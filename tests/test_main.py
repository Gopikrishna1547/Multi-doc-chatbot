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


class TestChatHistory:
    """Tests for chat_history module."""

    def test_format_empty_history(self):
        """Test that empty history returns default message."""
        result = format_chat_history([])
        assert "No conversation history" in result

    def test_format_chat_history_returns_string(self):
        """Test that format_chat_history returns a string."""
        history = [
            {"role": "user", "content": "What is Python?"},
            {"role": "assistant", "content": "Python is a programming language.", "sources": ["doc.pdf"]}
        ]
        result = format_chat_history(history)
        assert isinstance(result, str)
        assert "What is Python?" in result

    def test_get_chat_summary_correct_counts(self):
        """Test that get_chat_summary returns correct message counts."""
        history = [
            {"role": "user", "content": "Question 1"},
            {"role": "assistant", "content": "Answer 1", "sources": []},
            {"role": "user", "content": "Question 2"},
            {"role": "assistant", "content": "Answer 2", "sources": []}
        ]
        summary = get_chat_summary(history)
        assert summary["questions_asked"] == 2
        assert summary["answers_given"] == 2
        assert summary["total_messages"] == 4

    def test_clear_chat_history(self):
        """Test that clear_chat_history empties the chat list."""
        mock_state = MagicMock()
        mock_state.chat_history = [{"role": "user", "content": "test"}]
        clear_chat_history(mock_state)
        assert mock_state.chat_history == []
