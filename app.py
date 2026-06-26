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
