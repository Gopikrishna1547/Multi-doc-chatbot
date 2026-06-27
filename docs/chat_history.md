# Feature: Chat History Module

## Feature Branch
feature/chat-history

## Purpose
Handles all chat history operations including formatting, saving as PDF, clearing, and summarising conversation statistics.

## Functions

### format_chat_history(chat_history)
- Input: list of message dictionaries
- Output: formatted text string
- Labels messages as You or Assistant
- Includes source documents for each answer

### save_chat_as_pdf(chat_history, topic)
- Input: list of messages, optional topic string
- Output: file path of generated PDF
- Creates reports/ directory if not exists
- Timestamps filename to avoid overwrites
- Uses ReportLab for PDF generation

### clear_chat_history(session_state)
- Input: Streamlit session state object
- Clears chat_history list from session state
- Logs the clear action

### get_chat_summary(chat_history)
- Input: list of message dictionaries
- Output: dictionary with total, questions, answers count
- Used to show statistics in sidebar

## Dependencies
- reportlab
- datetime (built-in)
- logging (built-in)
