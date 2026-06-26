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
