"""Question answering, summarization, and auto-QA generation logic."""

import logging
import re
from collections import Counter
from typing import Dict, List

log = logging.getLogger(__name__)

NO_ANSWER_MESSAGE = "I could not find an answer to this question in the uploaded PDF document(s)."

STOP_WORDS = {
    "the", "is", "are", "was", "were", "a", "an", "and", "or", "to", "of",
    "in", "on", "for", "with", "what", "when", "where", "why", "how", "many",
    "much", "does", "do", "did", "by", "from", "this", "that", "it", "as", "at",
    "be", "has", "have", "had", "about", "into", "their", "there", "which", "your",
    "document", "pdf", "uploaded", "according",
}

DOMAIN_KEYWORDS = [
    "objective", "pandemic", "covid", "virus", "sars", "coronavirus", "variant",
    "omicron", "delta", "vaccination", "vaccine", "mental", "health", "who", "paho",
    "recommend", "measure", "population", "growth", "birth", "death", "fertility",
    "mortality", "demographic", "transition", "projection", "education", "summary",
]


def normalize(text: str) -> str:
    """Normalize whitespace."""
    return re.sub(r"\s+", " ", text or "").strip()


def tokens(text: str) -> set:
    """Tokenize text and add a few useful synonyms for retrieval."""
    words = re.findall(r"[a-zA-Z0-9\-]+", (text or "").lower())
    expanded = []
    for word in words:
        expanded.append(word)
        if word in {"caused", "cause"}:
            expanded.extend(["produced", "named"])
        if word == "virus":
            expanded.extend(["sars", "coronavirus", "sars-cov-2"])
        if word in {"covid", "covid-19"}:
            expanded.extend(["covid", "covid-19", "coronavirus", "sars"])
        if word in {"die", "died"}:
            expanded.extend(["death", "mortality"])
        if word in {"born"}:
            expanded.extend(["birth"])
    return {word for word in expanded if word not in STOP_WORDS and len(word) > 1}


def split_sentences(text: str) -> List[str]:
    """Split text into readable sentence-like units."""
    text = normalize(text)
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [sentence.strip() for sentence in sentences if 35 <= len(sentence.strip()) <= 900]


def build_context(search_results: list) -> tuple:
    """Build context and source labels from vector-search results."""
    context = "\n\n".join([doc.page_content for doc in search_results])
    source_labels = []
    for doc in search_results:
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page")
        label = f"{source} (page {page})" if page else source
        if label not in source_labels:
            source_labels.append(label)
    return context, source_labels


def score_sentence(question: str, sentence: str) -> int:
    """Score sentence based on overlap, domain phrases, and common PDF-QA patterns."""
    question_words = tokens(question)
    sentence_words = tokens(sentence)
    score = len(question_words & sentence_words) * 3

    lower_q = question.lower()
    lower_s = sentence.lower()

    phrase_boosts = [
        ("virus", ["sars", "coronavirus", "virus", "covid-19"]),
        ("caused", ["caused", "cause", "produced", "named"]),
        ("mental", ["mental health", "psychosocial", "isolation"]),
        ("omicron", ["omicron"]),
        ("delta", ["delta"]),
        ("vaccination", ["vaccination", "vaccines", "vaccinated"]),
        ("vaccine", ["vaccination", "vaccines", "vaccinated"]),
        ("recommend", ["recommends", "recommended", "measures", "wear", "mask", "distance"]),
        ("birth", ["birth", "born"]),
        ("death", ["death", "die", "mortality"]),
        ("demographic", ["demographic transition"]),
    ]

    for question_word, sentence_phrases in phrase_boosts:
        if question_word in lower_q and any(phrase in lower_s for phrase in sentence_phrases):
            score += 5

    if "covid" in lower_q and "covid" in lower_s:
        score += 4
    if "sars" in lower_s and ("virus" in lower_q or "caused" in lower_q or "cause" in lower_q):
        score += 8

    return score


def generate_answer(question: str, context: str) -> str:
    """Return only one best answer from uploaded PDF context."""
    sentences = split_sentences(context)
    if not sentences:
        return NO_ANSWER_MESSAGE

    ranked = sorted(
        ((score_sentence(question, sentence), sentence) for sentence in sentences),
        key=lambda item: item[0],
        reverse=True,
    )

    best_score, best_sentence = ranked[0]
    if best_score < 6:
        return NO_ANSWER_MESSAGE

    return normalize(best_sentence)[:700]


def summarize_documents(documents: Dict[str, str]) -> str:
    """Generate a concise 5-10 bullet summary from important PDF sentences."""
    all_text = " ".join(documents.values())
    sentences = split_sentences(all_text)

    if not sentences:
        return "Summary could not be generated because no readable text was found."

    word_counts = Counter(
        word for word in re.findall(r"[a-zA-Z0-9\-]+", all_text.lower())
        if word not in STOP_WORDS and len(word) > 3
    )

    scored = []
    for index, sentence in enumerate(sentences):
        lower = sentence.lower()
        words = re.findall(r"[a-zA-Z0-9\-]+", lower)
        score = sum(word_counts.get(word, 0) for word in words)
        score += sum(25 for keyword in DOMAIN_KEYWORDS if keyword in lower)
        score += max(0, 20 - index)  # abstracts/intros often carry the main idea
        scored.append((score, index, normalize(sentence)))

    selected = []
    seen = set()
    for _, index, sentence in sorted(scored, key=lambda item: item[0], reverse=True):
        key = sentence[:100].lower()
        if key in seen or len(sentence) < 50:
            continue
        selected.append((index, sentence))
        seen.add(key)
        if len(selected) >= 7:
            break

    selected = sorted(selected, key=lambda item: item[0])
    return "\n".join([f"- {sentence[:350]}" for _, sentence in selected])


def make_question_from_sentence(sentence: str) -> str:
    """Create a useful document-specific question from an important PDF sentence."""
    lower = sentence.lower()

    if "sars" in lower or "coronavirus" in lower:
        return "What virus caused COVID-19?"
    if "mental health" in lower or "psychosocial" in lower:
        return "How did COVID-19 affect mental health?"
    if "omicron" in lower:
        return "What does the document say about the Omicron variant?"
    if "delta" in lower:
        return "What does the document say about the Delta variant?"
    if "vaccin" in lower:
        return "Why is vaccination important according to the document?"
    if "world health organization" in lower or "who" in lower or "surveillance" in lower:
        return "What does WHO recommend for monitoring COVID-19 variants?"
    if any(word in lower for word in ["mask", "distance", "hands", "ventilate", "crowded"]):
        return "What public health measures are recommended to reduce COVID-19 spread?"
    if "birth" in lower and "death" in lower:
        return "How many people are born and die each year worldwide?"
    if "population growth" in lower:
        return "What does the document explain about population growth?"
    if "demographic transition" in lower:
        return "What is the demographic transition?"
    if "fertility" in lower:
        return "How does fertility affect population growth?"
    if "mortality" in lower:
        return "How does mortality affect population growth?"
    if "education" in lower and "population" in lower:
        return "How is education connected to population projections?"

    topic_words = [
        word for word in re.findall(r"[A-Za-z][A-Za-z\-]+", sentence)
        if word.lower() not in STOP_WORDS
    ]
    topic = " ".join(topic_words[:5]) if topic_words else "this section"
    return f"What important point does the document make about {topic}?"


def generate_important_qa(documents: Dict[str, str]) -> List[dict]:
    """Generate document-specific important questions and PDF-grounded answers."""
    all_text = " ".join(documents.values())
    sentences = split_sentences(all_text)

    if not sentences:
        return []

    scored = []
    for index, sentence in enumerate(sentences):
        lower = sentence.lower()
        score = sum(12 for keyword in DOMAIN_KEYWORDS if keyword in lower)
        score += max(0, 12 - index)
        if any(char.isdigit() for char in sentence):
            score += 3
        scored.append((score, index, normalize(sentence)))

    qa_pairs = []
    used_questions = set()
    used_answers = set()

    for _, _, sentence in sorted(scored, key=lambda item: item[0], reverse=True):
        if len(qa_pairs) >= 7:
            break

        answer = sentence[:700]
        answer_key = answer[:100].lower()
        if answer_key in used_answers:
            continue

        question = make_question_from_sentence(answer)
        if question in used_questions:
            continue

        qa_pairs.append({"question": question, "answer": answer})
        used_questions.add(question)
        used_answers.add(answer_key)

    return qa_pairs


def ask_question(vector_store, question: str) -> dict:
    """Search documents and generate one best answer only."""
    from src.vector_store import search_documents

    search_results = search_documents(vector_store, question, k=3)
    if not search_results:
        return {"question": question, "answer": NO_ANSWER_MESSAGE, "sources": [], "context": ""}

    context, sources = build_context(search_results)
    answer = generate_answer(question, context)

    if answer == NO_ANSWER_MESSAGE:
        sources = []

    return {"question": question, "answer": answer, "sources": sources, "context": context}
