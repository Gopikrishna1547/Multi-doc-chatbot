import logging
from transformers import pipeline

log = logging.getLogger(__name__)
_qa_pipeline = None


def get_qa_pipeline():
    """Load and return QA pipeline — loaded once and cached."""
    global _qa_pipeline
    if _qa_pipeline is None:
        log.info("Loading QA model...")
        _qa_pipeline = pipeline(
            "question-answering",
            model="deepset/roberta-base-squad2"
        )
        log.info("QA model loaded successfully")
    return _qa_pipeline


def build_context(search_results: list) -> tuple:
    """Build context string and source list from search results."""
    log.info("Building context from search results")
    context = "\n\n".join([doc.page_content for doc in search_results])
    sources = list(set([
        doc.metadata.get("source", "Unknown")
        for doc in search_results
    ]))
    return context, sources
