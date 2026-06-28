"""Streamlit application for the Multi-Document AI Assistant."""

import logging

import streamlit as st

from src.pdf_loader import get_document_stats, load_multiple_pdfs
from src.qa_engine import (
    ask_question,
    generate_important_qa_by_file,
    summarize_documents_by_file,
)
from src.vector_store import build_vector_store, split_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)

MAX_UPLOADS = 5

st.set_page_config(page_title="Multi-Document AI Assistant", page_icon="🤖", layout="wide")


def init_session_state():
    """Initialize all Streamlit session state variables."""
    defaults = {
        "vector_store": None,
        "chat_history": [],
        "documents_loaded": False,
        "document_names": [],
        "document_summaries": {},
        "document_questions": {},
        "document_stats": {"documents": 0, "pages": 0, "words": 0, "chunks": 0},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def count_chunks(documents: dict) -> int:
    """Count chunks generated from loaded documents."""
    total = 0
    for name, text in documents.items():
        total += len(split_text(text, name))
    return total


def render_sidebar():
    """Render sidebar upload controls and document list."""
    with st.sidebar:
        st.title("📂 Documents")
        st.markdown("Upload up to **5 PDFs** and ask questions based only on uploaded content.")
        st.divider()

        uploaded_files = st.file_uploader(
            "Upload PDF documents",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload up to 5 text-based PDF files.",
        )

        if uploaded_files and len(uploaded_files) > MAX_UPLOADS:
            st.error(f"Maximum {MAX_UPLOADS} PDF files are allowed. Please remove extra files.")
            return

        if uploaded_files and st.button("Process Documents", type="primary"):
            with st.spinner("Reading PDFs and building search index..."):
                try:
                    documents = load_multiple_pdfs(uploaded_files)
                    stats = get_document_stats(documents)
                    stats["chunks"] = count_chunks(documents)

                    st.session_state.vector_store = build_vector_store(documents)
                    st.session_state.documents_loaded = True
                    st.session_state.document_names = list(documents.keys())
                    st.session_state.document_stats = stats
                    st.session_state.chat_history = []
                    st.session_state.document_summaries = summarize_documents_by_file(documents)
                    st.session_state.document_questions = generate_important_qa_by_file(documents)

                    st.success(f"Loaded {len(documents)} document(s).")
                except Exception as error:
                    st.error(f"Error processing documents: {error}")
                    log.exception("Document processing failed")

        if st.session_state.documents_loaded:
            st.divider()
            st.markdown("### ✅ Loaded Documents")
            for index, name in enumerate(st.session_state.document_names, start=1):
                st.markdown(f"{index}. {name}")


def render_stats():
    """Render document statistics cards."""
    stats = st.session_state.document_stats
    questions_asked = sum(1 for item in st.session_state.chat_history if item.get("role") == "user")

    st.markdown("### 📊 Document Statistics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("PDFs", stats.get("documents", 0))
    col2.metric("Pages", stats.get("pages", 0))
    col3.metric("Chunks", stats.get("chunks", 0))
    col4.metric("Questions", questions_asked)


def render_document_sections():
    """Render per-document summary and per-document generated questions."""
    st.markdown("## 📄 Summaries by Document")
    for index, name in enumerate(st.session_state.document_names, start=1):
        with st.expander(f"{index}. {name} — Summary", expanded=index == 1):
            bullets = st.session_state.document_summaries.get(name, [])
            for bullet in bullets:
                st.markdown(f"- {bullet}")

    st.markdown("## ❓ Important Questions by Document")
    for index, name in enumerate(st.session_state.document_names, start=1):
        with st.expander(f"{index}. {name} — Questions", expanded=index == 1):
            questions = st.session_state.document_questions.get(name, [])
            if not questions:
                st.info("No questions could be generated for this document.")
            for q_index, item in enumerate(questions, start=1):
                st.markdown(f"**Q{q_index}: {item['question']}**")
                st.markdown(item["answer"])
                st.divider()


def render_chat():
    """Render the main chat interface."""
    st.title("🤖 Multi-Document AI Assistant")
    st.caption(
        "Upload up to 5 PDFs, view a separate summary and questions for every document, "
        "and receive page-based answers only from uploaded PDF content."
    )

    if not st.session_state.documents_loaded:
        st.info("👈 Upload one or more PDF documents from the sidebar to begin.")
        st.markdown(
            """
### 🚀 Features

- 📂 Upload up to 5 PDF documents
- 📄 Get a 5-7 line summary for each document
- ❓ Get important questions for each document
- 💬 Ask your own questions
- 📌 See source PDF name and page number
- 📚 If multiple pages are relevant, see separate page-based answers
- 🚫 Get a clear fallback message when the answer is not in the PDFs
"""
        )
        return

    render_stats()
    st.divider()
    render_document_sections()

    st.divider()
    st.markdown("## 💬 Ask Your Own Question")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and message.get("sources"):
                st.caption(f"Sources: {', '.join(message['sources'])}")

    question = st.chat_input("Ask a question about your uploaded PDF documents...")

    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})

        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                try:
                    result = ask_question(st.session_state.vector_store, question)
                    answer = result["answer"]
                    sources = result["sources"]

                    st.markdown(answer)
                    if sources:
                        st.caption(f"Sources: {', '.join(sources)}")

                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": answer, "sources": sources}
                    )
                except Exception as error:
                    error_msg = f"Error generating answer: {error}"
                    st.error(error_msg)
                    log.exception(error_msg)


def main():
    """Main application entry point."""
    init_session_state()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()
