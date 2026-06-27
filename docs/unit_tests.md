# Feature: Unit Tests

## Feature Branch
feature/unit-tests

## Purpose
Unit tests for all modules in the Multi-Document Chatbot project. Ensures each function works correctly in isolation.

## Test Classes

### TestPdfLoader
- test_load_multiple_pdfs_returns_dict
- test_load_multiple_pdfs_empty_list
- test_load_multiple_pdfs_correct_keys

### TestVectorStore
- test_split_text_returns_list
- test_split_text_metadata_contains_source
- test_split_text_empty_string

### TestChatHistory
- test_format_empty_history
- test_format_chat_history_returns_string
- test_get_chat_summary_correct_counts
- test_clear_chat_history

## How to Run Tests
```bash
pytest tests/test_main.py -v
```

## Dependencies
- pytest
- unittest.mock (built-in)
