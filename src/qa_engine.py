import logging

log = logging.getLogger(__name__)


def build_context(search_results: list) -> tuple:
    """Build context string and source list from search results."""
    log.info("Building context from search results")
    context = "\n\n".join([doc.page_content for doc in search_results])
    sources = list(set([
        doc.metadata.get("source", "Unknown")
        for doc in search_results
    ]))
    return context, sources


def generate_answer(question: str, context: str) -> str:
    """Find the most relevant sentence from context as the answer."""
    log.info(f"Finding answer for: {question}")
    try:
        question_words = set(question.lower().split())
        sentences = []
        for chunk in context.split("\n"):
            chunk = chunk.strip()
            if len(chunk) > 30:
                sentences.append(chunk)

        if not sentences:
            return "No relevant content found in the documents."

        best_sentence = ""
        best_score = 0
        for sentence in sentences:
            sentence_words = set(sentence.lower().split())
            score = len(question_words & sentence_words)
            if score > best_score:
                best_score = score
                best_sentence = sentence

        if best_sentence:
            return best_sentence[:500]
        return sentences[0][:500]

    except Exception as e:
        log.error(f"Answer generation failed: {e}")
        return "Could not generate an answer. Please try rephrasing."


def ask_question(vector_store, question: str) -> dict:
    """Full pipeline: search documents and generate answer."""
    from src.vector_store import search_documents
    log.info(f"Processing question: {question}")
    search_results = search_documents(vector_store, question, k=4)
    context, sources = build_context(search_results)
    answer = generate_answer(question, context)
    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "context": context
    }
