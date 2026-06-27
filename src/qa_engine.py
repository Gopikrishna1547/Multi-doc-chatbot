import logging
import re
from collections import Counter

log = logging.getLogger(__name__)

NO_ANSWER_MESSAGE = "I could not find an answer to this question in the uploaded PDF document(s)."


def build_context(search_results: list) -> tuple:
    """Build context string and source list from search results."""
    log.info("Building context from search results")
    context = "\n\n".join([doc.page_content for doc in search_results])
    sources = list(set([
        doc.metadata.get("source", "Unknown")
        for doc in search_results
    ]))
    return context, sources


def split_sentences(text: str) -> list:
    """Split text into readable sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 40]


def score_sentence(question: str, sentence: str) -> int:
    """Score sentence based on word overlap with question."""
    question_words = set(re.findall(r"\w+", question.lower()))
    sentence_words = set(re.findall(r"\w+", sentence.lower()))

    stop_words = {
        "the", "is", "are", "was", "were", "a", "an", "and", "or", "to",
        "of", "in", "on", "for", "with", "what", "when", "where", "why",
        "how", "many", "much", "does", "do", "did", "by", "from", "this",
        "that", "it", "as", "at"
    }

    question_words = question_words - stop_words
    sentence_words = sentence_words - stop_words

    return len(question_words & sentence_words)


def generate_answer(question: str, context: str) -> str:
    """Return only one best answer from context."""
    log.info(f"Finding answer for: {question}")

    sentences = split_sentences(context)

    if not sentences:
        return NO_ANSWER_MESSAGE

    best_sentence = ""
    best_score = 0

    for sentence in sentences:
        score = score_sentence(question, sentence)
        if score > best_score:
            best_score = score
            best_sentence = sentence

    if best_score < 1:
        return NO_ANSWER_MESSAGE

    return best_sentence[:700]


def summarize_documents(documents: dict) -> str:
    """Generate a concise extractive summary from uploaded PDFs."""
    all_text = " ".join(documents.values())
    sentences = split_sentences(all_text)

    if not sentences:
        return "Summary could not be generated because no readable text was found."

    words = re.findall(r"\w+", all_text.lower())
    stop_words = {
        "the", "is", "are", "was", "were", "a", "an", "and", "or", "to",
        "of", "in", "on", "for", "with", "by", "from", "this", "that",
        "it", "as", "at", "be", "has", "have", "had"
    }

    important_words = [w for w in words if w not in stop_words and len(w) > 3]
    word_counts = Counter(important_words)

    scored_sentences = []
    for sentence in sentences:
        sentence_words = re.findall(r"\w+", sentence.lower())
        score = sum(word_counts.get(word, 0) for word in sentence_words)
        scored_sentences.append((score, sentence))

    top_sentences = sorted(scored_sentences, reverse=True)[:5]

    summary_lines = [f"- {sentence}" for _, sentence in top_sentences]
    return "\n".join(summary_lines)


def generate_important_qa(documents: dict) -> list:
    """Generate important questions and answers from PDF text."""
    all_text = " ".join(documents.values())
    sentences = split_sentences(all_text)

    if not sentences:
        return []

    selected_sentences = sentences[:5]
    qa_pairs = []

    question_templates = [
        "What is the main topic discussed in the document?",
        "What important information is mentioned in the document?",
        "What key point does the document explain?",
        "What fact is highlighted in the uploaded PDF?",
        "What conclusion can be understood from the document?"
    ]

    for index, sentence in enumerate(selected_sentences):
        qa_pairs.append({
            "question": question_templates[index],
            "answer": sentence[:700]
        })

    return qa_pairs


def ask_question(vector_store, question: str) -> dict:
    """Full pipeline: search documents and generate one best answer."""
    from src.vector_store import search_documents

    log.info(f"Processing question: {question}")

    search_results = search_documents(vector_store, question, k=1)

    if not search_results:
        return {
            "question": question,
            "answer": NO_ANSWER_MESSAGE,
            "sources": [],
            "context": ""
        }

    context, sources = build_context(search_results)
    answer = generate_answer(question, context)

    if answer == NO_ANSWER_MESSAGE:
        sources = []

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "context": context
    }
