import logging
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

log = logging.getLogger(__name__)


def get_embeddings():
    """Load and return Hugging Face sentence transformer embeddings."""
    log.info("Loading embedding model...")
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def split_text(text: str, source_name: str) -> list:
    """Split text into chunks and tag each chunk with source document name."""
    log.info(f"Splitting text from: {source_name}")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.create_documents(
        texts=[text],
        metadatas=[{"source": source_name}]
    )
    log.info(f"Created {len(chunks)} chunks from {source_name}")
    return chunks


def build_vector_store(documents: dict) -> object:
    """Build FAISS vector store from multiple documents."""
    log.info(f"Building vector store from {len(documents)} documents")
    all_chunks = []
    for name, text in documents.items():
        chunks = split_text(text, name)
        all_chunks.extend(chunks)
    embeddings = get_embeddings()
    vector_store = FAISS.from_documents(all_chunks, embeddings)
    log.info(f"Vector store built with {len(all_chunks)} total chunks")
    return vector_store


def search_documents(vector_store, query: str, k: int = 4) -> list:
    """Search vector store and return top k most relevant chunks."""
    log.info(f"Searching for: {query}")
    results = vector_store.similarity_search(query, k=k)
    log.info(f"Found {len(results)} relevant chunks")
    return results
