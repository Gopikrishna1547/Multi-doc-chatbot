"""Streamlit application for the Multi-Document AI Assistant."""

import logging

import streamlit as st

from src.pdf_loader import get_document_stats, load_multiple_pdfs
from src.qa_engine import ask_question, generate_important_qa, summarize_documents
from src.vector_store import build_vector_store, split_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)
log = logging.getLogger(__name__)

st.set_page_config(page_title="Multi-Document AI Assistant", page_icon="🤖", layout="wide")


def init_session_state():
    """Initialize all Streamlit session state variables."""
    defaults = {
        "vector_store": None,
        "chat_history": [],
        "documents_loaded": False,
        "document_names": [],
        "document_summary": "",
        "auto_qa": [],
        "document_stats": {"documents": 0, "pages": 0, "words": 0, "chunks": 0},
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def count_chunks(documents: dict) -> int:
    """Count text chunks without building another vector store."""
    total = 0
    for name, text in documents.items():
        total += len(split_text(text, name))
    return total


def render_sidebar():
    """Render sidebar upload controls and document list."""
    with st.sidebar:
        st.title("📂 Documents")
        st.markdown("Upload PDFs and ask questions based only on uploaded content.")
        st.divider()

        uploaded_files = st.file_uploader(
            "Upload PDF documents",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload one or more text-based PDF files.",
        )

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
                    st.session_state.document_summary = summarize_documents(documents)
                    st.session_state.auto_qa = generate_important_qa(documents)

                    st.success(f"Loaded {len(documents)} document(s).")
                except Exception as error:
                    st.error(f"Error processing documents: {error}")
                    log.exception("Document processing failed")

        if st.session_state.documents_loaded:
            st.divider()
            st.markdown("### ✅ Loaded Documents")
            for name in st.session_state.document_names:
                st.markdown(f"- {name}")


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


def render_chat():
    """Render the main chat interface."""
    st.title("🤖 Multi-Document AI Assistant")
    st.caption(
        "Upload PDFs, generate a short summary, review important questions, "
        "and ask questions answered only from uploaded PDF content."
    )

    if not st.session_state.documents_loaded:
        st.info("👈 Upload one or more PDF documents from the sidebar to begin.")
        st.markdown(
            """
### 🚀 Features

- 📂 Upload multiple PDF documents
- 📄 Generate a concise 5-10 point summary
- ❓ Generate important document-specific questions
- 💬 Ask your own questions
- 🎯 Receive one best answer from the uploaded PDF(s)
- 🚫 Get a clear fallback message when the answer is not in the PDFs
"""
        )
        return

    render_stats()
    st.divider()

    if st.session_state.document_summary:
        st.markdown("## 📄 PDF Summary")
        st.markdown(st.session_state.document_summary)

    if st.session_state.auto_qa:
        st.markdown("## ❓ Important Questions and Answers")
        for index, item in enumerate(st.session_state.auto_qa, start=1):
            with st.expander(f"Q{index}: {item['question']}"):
                st.write(item["answer"])

    st.divider()
    st.markdown("## 💬 Ask Your Own Question")

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
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

                    st.write(answer)
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
