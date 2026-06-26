import logging
import streamlit as st
from src.pdf_loader import load_multiple_pdfs
from src.vector_store import build_vector_store
from src.qa_engine import ask_question

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
    if "document_names" not in st.session_state:
        st.session_state.document_names = []


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
                    st.success(f"Loaded {len(documents)} documents!")
                except Exception as e:
                    st.error(f"Error processing documents: {e}")

        if st.session_state.documents_loaded:
            st.divider()
            st.markdown("**Loaded Documents:**")
            for name in st.session_state.document_names:
                st.markdown(f"- {name}")
