# Feature: Chat Interface Module

## Feature Branch
feature/chat-interface

## Purpose
Provides the Streamlit web interface for the Multi-Document Chatbot. Handles PDF upload, document processing, and interactive chat.

## Functions

### init_session_state()
- Initializes all session state variables
- vector_store: FAISS vector store object
- chat_history: list of message dictionaries
- documents_loaded: boolean flag
- document_names: list of uploaded file names

### render_sidebar()
- PDF file uploader (multiple files)
- Process Documents button
- Calls load_multiple_pdfs and build_vector_store
- Shows list of loaded document names

### render_chat()
- Displays full conversation history
- Shows source document for each answer
- Chat input box at bottom
- Calls ask_question for each user message

### main()
- Entry point for the application
- Calls init_session_state, render_sidebar, render_chat

## Dependencies
- streamlit
- src/pdf_loader.py
- src/vector_store.py
- src/qa_engine.py
