"""Vector-store utilities for document retrieval."""

import logging
import re
from dataclasses import dataclass
from typing import List

log = logging.getLogger(__name__)


@dataclass
class SimpleDocument:
    """Small fallback document object used when LangChain is unavailable in tests."""

    page_content: str
    metadata: dict


def get_embeddings():
    """Load and return Hugging Face sentence-transformer embeddings."""
    from langchain_community.embeddings import HuggingFaceEmbeddings

    log.info("Loading embedding model...")
    return HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")


def _split_pages(text: str) -> List[tuple[int, str]]:
    """Split marked PDF text into (page_number, page_text) pairs."""
    matches = list(re.finditer(r"\[PAGE (\d+)\]", text or ""))
    if not matches:
        return [(1, text or "")]

    pages = []
    for index, match in enumerate(matches):
        page_number = int(match.group(1))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        page_text = text[start:end].strip()
        pages.append((page_number, page_text))
    return pages


def _basic_split(text: str, chunk_size: int = 650, overlap: int = 100) -> List[str]:
    """Fallback text splitter used when langchain-text-splitters is unavailable."""
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks


def split_text(text: str, source_name: str) -> list:
    """Split text into chunks tagged with source document and page number."""
    log.info("Splitting text from: %s", source_name)

    try:
        from langchain_core.documents import Document
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(chunk_size=650, chunk_overlap=100)
        use_langchain = True
    except ImportError:
        Document = SimpleDocument
        splitter = None
        use_langchain = False

    chunks = []
    for page_number, page_text in _split_pages(text):
        if not page_text:
            continue

        metadata = {"source": source_name, "page": page_number}
        if use_langchain:
            chunks.extend(splitter.create_documents(texts=[page_text], metadatas=[metadata]))
        else:
            chunks.extend(SimpleDocument(chunk, metadata) for chunk in _basic_split(page_text))

    log.info("Created %s chunks from %s", len(chunks), source_name)
    return chunks


def build_vector_store(documents: dict) -> object:
    """Build FAISS vector store from multiple documents."""
    from langchain_community.vectorstores import FAISS

    log.info("Building vector store from %s documents", len(documents))
    all_chunks = []

    for name, text in documents.items():
        all_chunks.extend(split_text(text, name))

    if not all_chunks:
        raise ValueError("No readable PDF text found. Please upload text-based PDF documents.")

    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(all_chunks, embeddings)
    log.info("Vector store built with %s total chunks", len(all_chunks))
    return vector_store


def search_documents(vector_store, query: str, k: int = 4) -> list:
    """Search vector store and return top k most relevant chunks."""
    log.info("Searching for: %s", query)
    results = vector_store.similarity_search(query, k=k)
    log.info("Found %s relevant chunks", len(results))
    return results
