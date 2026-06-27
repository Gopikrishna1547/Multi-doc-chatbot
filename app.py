import logging
import streamlit as st
from src.pdf_loader import load_multiple_pdfs
from src.vector_store import build_vector_store
from src.qa_engine import ask_question, summarize_documents, generate_important_qa
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
log = logging.getLogger(__name__)

st.set_page_config(
    page_title="Multi-Document Chatbot",
    page_icon="AI",
    layout="wide"
)


def init_session_state():
    """Initialize all Streamlit session state variables."""
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "documents_loaded" not in st.session_state:
        st.session_state.documents_loaded = False    
if "document_summary" not in st.session_state:
    st.session_state.document_summary = ""

if "auto_qa" not in st.session_state:
    st.session_state.auto_qa = []
def render_sidebar():
    """Render the sidebar with PDF upload and document info."""
    with st.sidebar:
        st.title("Multi-Document Chatbot")
        st.markdown("Upload PDFs and ask questions across all documents.")
        st.divider()

        uploaded_files = st.file_uploader(
            "Upload PDF documents",
            type=["pdf"],
            accept_multiple_files=True,
            help="Upload 2-10 PDF files"
        )

        if uploaded_files and st.button("Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                try:
                    documents = load_multiple_pdfs(uploaded_files)
                    st.session_state.vector_store = build_vector_store(documents)
                    st.session_state.documents_loaded = True
                    st.session_state.document_names = list(documents.keys())
                    st.session_state.chat_history = []

                    st.session_state.document_summary = summarize_documents(documents)
                    st.session_state.auto_qa = generate_important_qa(documents)

                    st.success(f"Loaded {len(documents)} documents!")
                except Exception as e:
                    st.error(f"Error processing documents: {e}")
        if st.session_state.documents_loaded:
            st.divider()
            st.markdown("**Loaded Documents:**")
            for name in st.session_state.document_names:
                st.markdown(f"- {name}")


def render_chat():
    """Render the main chat interface."""
    st.title("Multi-Document Chatbot")

    if not st.session_state.documents_loaded:
        st.info("Upload PDF documents in the sidebar to get started.")
        st.markdown("### What you can do:")
        st.markdown("""
        - Upload multiple PDF documents at once
        - Ask questions across all documents
        - See which document the answer came from
        - View conversation history
        """)
        return
    if st.session_state.document_summary:
        st.subheader("PDF Summary")
        st.markdown(st.session_state.document_summary)

    if st.session_state.auto_qa:
        st.subheader("Important Questions and Answers")
        for i, item in enumerate(st.session_state.auto_qa, start=1):
            with st.expander(f"Q{i}: {item['question']}"):
                st.write(item["answer"])
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if message["role"] == "assistant" and "sources" in message:
                if message["sources"]:
                    st.caption(f"Sources: {', '.join(message['sources'])}")

    question = st.chat_input("Ask a question about your documents...")

    if question:
        st.session_state.chat_history.append({
            "role": "user",
            "content": question
        })
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents..."):
                try:
                    result = ask_question(
                        st.session_state.vector_store,
                        question
                    )
                    answer = result["answer"]
                    sources = result["sources"]
                    st.write(answer)
                    if sources:
                        st.caption(f"Sources: {', '.join(sources)}")
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                except Exception as e:
                    error_msg = f"Error generating answer: {e}"
                    st.error(error_msg)
                    log.error(error_msg)


def main():
    """Main entry point for the Streamlit application."""
    init_session_state()
    render_sidebar()
    render_chat()


if __name__ == "__main__":
    main()


def render_chat_controls():
    """Render chat history controls in sidebar."""
    from src.chat_history import save_chat_as_pdf, clear_chat_history, get_chat_summary
    import streamlit as st

    if st.session_state.chat_history:
        st.sidebar.divider()
        summary = get_chat_summary(st.session_state.chat_history)
        st.sidebar.markdown(f"**Questions asked:** {summary['questions_asked']}")

        if st.sidebar.button("Download Chat as PDF"):
            with st.spinner("Generating PDF..."):
                path = save_chat_as_pdf(st.session_state.chat_history)
                with open(path, "rb") as f:
                    st.sidebar.download_button(
                        label="Click to Download",
                        data=f,
                        file_name="chat_history.pdf",
                        mime="application/pdf"
                    )

        if st.sidebar.button("Clear Chat History"):
            clear_chat_history(st.session_state)
            st.rerun()
