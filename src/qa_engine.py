"""Question answering, summarization, and per-document auto-QA logic."""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Tuple

log = logging.getLogger(__name__)

NO_ANSWER_MESSAGE = "I could not find an answer to this question in the uploaded PDF document(s)."

STOP_WORDS = {
    "the", "is", "are", "was", "were", "a", "an", "and", "or", "to", "of",
    "in", "on", "for", "with", "what", "when", "where", "why", "how", "many",
    "much", "does", "do", "did", "by", "from", "this", "that", "it", "as", "at",
    "be", "has", "have", "had", "about", "into", "their", "there", "which", "your",
    "document", "pdf", "uploaded", "according", "give", "tell", "me", "can", "you",
}

IMPORTANT_KEYWORDS = [
    "objective", "pandemic", "covid", "virus", "sars", "coronavirus", "variant",
    "omicron", "delta", "vaccination", "vaccine", "mental", "health", "who", "paho",
    "recommend", "measure", "population", "growth", "birth", "death", "fertility",
    "mortality", "demographic", "transition", "projection", "education", "migration",
    "density", "children", "doubling", "billion", "million", "un", "country", "region",
]


# ---------- Shared helpers ----------

def normalize(text: str) -> str:
    """Normalize whitespace in extracted PDF text."""
    return re.sub(r"\s+", " ", text or "").strip()


def get_page_blocks(text: str) -> List[Tuple[int, str]]:
    """Split marked PDF text into (page_number, page_text) blocks."""
    matches = list(re.finditer(r"\[PAGE (\d+)\]", text or ""))
    if not matches:
        return [(1, text or "")]

    pages: List[Tuple[int, str]] = []
    for index, match in enumerate(matches):
        page_number = int(match.group(1))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        page_text = text[start:end].strip()
        if page_text:
            pages.append((page_number, page_text))
    return pages


def split_sentences(text: str) -> List[str]:
    """Split text into readable sentence-like units."""
    text = normalize(text)
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [sentence.strip() for sentence in sentences if 35 <= len(sentence.strip()) <= 900]


def numbers_in(text: str) -> set[str]:
    """Extract meaningful numeric tokens from text."""
    return set(re.findall(r"\b\d+(?:\.\d+)?\b", text or ""))


def tokens(text: str) -> set[str]:
    """Tokenize and add small domain synonyms for PDF QA."""
    words = re.findall(r"[a-zA-Z0-9\-]+", (text or "").lower())
    expanded: List[str] = []

    for word in words:
        expanded.append(word)
        if word in {"caused", "cause"}:
            expanded.extend(["produced", "named"])
        if word == "virus":
            expanded.extend(["sars", "sars-cov-2", "coronavirus"])
        if word in {"covid", "covid-19"}:
            expanded.extend(["covid", "covid-19", "coronavirus", "sars"])
        if word in {"die", "died", "deaths"}:
            expanded.extend(["death", "mortality"])
        if word in {"born", "births"}:
            expanded.extend(["birth", "born"])
        if word in {"people", "population"}:
            expanded.extend(["population", "people"])
        if word in {"recommend", "recommended", "recommendations"}:
            expanded.extend(["recommends", "measure", "measures"])

    return {word for word in expanded if word not in STOP_WORDS and len(word) > 1}


def source_label(doc) -> str:
    """Build a readable source label with file name and page number."""
    source = doc.metadata.get("source", "Unknown")
    page = doc.metadata.get("page")
    return f"{source} (page {page})" if page else source


# ---------- Summary and auto-question generation ----------

def score_summary_sentence(sentence: str, position: int) -> int:
    """Score sentences for summary usefulness."""
    lower = sentence.lower()
    score = 0
    score += sum(5 for keyword in IMPORTANT_KEYWORDS if keyword in lower)
    score += 4 if any(char.isdigit() for char in sentence) else 0
    score += max(0, 8 - position // 5)
    if len(sentence) > 350:
        score -= 4
    return score


def summarize_one_document(text: str, max_lines: int = 7) -> List[str]:
    """Generate a 5-7 bullet summary for one document only."""
    sentences = split_sentences(text)
    if not sentences:
        return ["No readable text was found in this PDF."]

    scored = []
    used = set()
    for index, sentence in enumerate(sentences):
        sentence = normalize(sentence)
        key = sentence[:120].lower()
        if key in used:
            continue
        used.add(key)
        scored.append((score_summary_sentence(sentence, index), index, sentence))

    selected: List[str] = []
    for _, _, sentence in sorted(scored, key=lambda item: item[0], reverse=True):
        selected.append(sentence[:350])
        if len(selected) >= max_lines:
            break

    if len(selected) < 5:
        for sentence in sentences:
            sentence = normalize(sentence)[:350]
            if sentence not in selected:
                selected.append(sentence)
            if len(selected) >= min(5, len(sentences)):
                break

    return selected[:max_lines]


def summarize_documents_by_file(documents: Dict[str, str]) -> Dict[str, List[str]]:
    """Return {document_name: [5-7 summary bullets]}."""
    return {name: summarize_one_document(text) for name, text in documents.items()}


def summarize_documents(documents: Dict[str, str]) -> str:
    """Backward-compatible combined markdown summary grouped by document."""
    grouped = summarize_documents_by_file(documents)
    sections = []
    for index, (name, bullets) in enumerate(grouped.items(), start=1):
        lines = [f"### {index}. {name}"]
        lines.extend(f"- {bullet}" for bullet in bullets)
        sections.append("\n".join(lines))
    return "\n\n".join(sections)


def make_question_from_sentence(sentence: str) -> str:
    """Create a useful document-specific question from an important PDF sentence."""
    lower = sentence.lower()

    if "birth" in lower and "death" in lower and "every year" in lower:
        return "How many people are born and die each year worldwide?"
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
        return "What does WHO recommend according to the document?"
    if any(word in lower for word in ["mask", "distance", "hands", "ventilate", "crowded"]):
        return "What public health measures are recommended?"
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
    if "doubl" in lower and "population" in lower:
        return "How often does the world population double?"
    if "asia" in lower and "region" in lower:
        return "Which world region has been the most populous?"

    topic_words = [
        word for word in re.findall(r"[A-Za-z][A-Za-z\-]+", sentence)
        if word.lower() not in STOP_WORDS
    ]
    topic = " ".join(topic_words[:5]) if topic_words else "this section"
    return f"What important point does the document make about {topic}?"


def generate_important_qa_for_text(text: str, max_questions: int = 5) -> List[dict]:
    """Generate document-specific questions and PDF-grounded answers for one document."""
    sentences = split_sentences(text)
    if not sentences:
        return []

    scored = []
    for index, sentence in enumerate(sentences):
        sentence = normalize(sentence)
        lower = sentence.lower()
        score = sum(10 for keyword in IMPORTANT_KEYWORDS if keyword in lower)
        score += max(0, 10 - index // 8)
        score += 3 if any(char.isdigit() for char in sentence) else 0
        scored.append((score, index, sentence))

    qa_pairs: List[dict] = []
    used_questions = set()
    used_answers = set()

    for _, _, sentence in sorted(scored, key=lambda item: item[0], reverse=True):
        question = make_question_from_sentence(sentence)
        answer = sentence[:700]
        answer_key = answer[:120].lower()
        if question in used_questions or answer_key in used_answers:
            continue
        qa_pairs.append({"question": question, "answer": answer})
        used_questions.add(question)
        used_answers.add(answer_key)
        if len(qa_pairs) >= max_questions:
            break

    return qa_pairs


def generate_important_qa_by_file(documents: Dict[str, str]) -> Dict[str, List[dict]]:
    """Return {document_name: [five useful QA pairs]}."""
    return {name: generate_important_qa_for_text(text, max_questions=5) for name, text in documents.items()}


def generate_important_qa(documents: Dict[str, str]) -> List[dict]:
    """Backward-compatible flat list of important QA pairs."""
    grouped = generate_important_qa_by_file(documents)
    result: List[dict] = []
    for name, items in grouped.items():
        for item in items:
            result.append({"document": name, **item})
    return result


# ---------- Answer matching ----------

def score_sentence(question: str, sentence: str) -> int:
    """Score a candidate answer sentence for a question."""
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
        ("birth", ["birth", "born", "births"]),
        ("born", ["birth", "born", "births"]),
        ("death", ["death", "deaths", "die", "mortality"]),
        ("die", ["death", "deaths", "die", "mortality"]),
        ("population", ["population", "people"]),
        ("demographic", ["demographic transition", "birth rate", "death rate"]),
    ]

    for question_term, answer_terms in phrase_boosts:
        if question_term in lower_q and any(term in lower_s for term in answer_terms):
            score += 5

    q_numbers = numbers_in(question)
    if q_numbers:
        # Require requested numeric values/years for numeric questions. This prevents
        # unrelated population paragraphs from answering exact-number questions.
        s_numbers = numbers_in(sentence)
        matched = q_numbers & s_numbers
        if matched:
            score += 8 * len(matched)
        else:
            score -= 10

    if "?" not in sentence and len(sentence) > 500:
        score -= 2

    return score


def best_sentence_for_chunk(question: str, chunk_text: str) -> Tuple[str, int]:
    """Return best sentence and score from one retrieved chunk."""
    best_sentence = ""
    best_score = 0
    for sentence in split_sentences(chunk_text):
        score = score_sentence(question, sentence)
        if score > best_score:
            best_score = score
            best_sentence = normalize(sentence)
    return best_sentence, best_score


def build_context(search_results: list) -> tuple:
    """Build context and source labels from search results."""
    context = "\n\n".join([doc.page_content for doc in search_results])
    labels = []
    for doc in search_results:
        label = source_label(doc)
        if label not in labels:
            labels.append(label)
    return context, labels


def generate_answer(question: str, context: str) -> str:
    """Backward-compatible one-answer generation from context."""
    best_sentence, best_score = best_sentence_for_chunk(question, context)
    if best_score < 6:
        return NO_ANSWER_MESSAGE
    return best_sentence[:900]


def ask_question(vector_store, question: str) -> dict:
    """Return best page answer(s), grounded only in uploaded PDFs."""
    from src.vector_store import search_documents

    search_results = search_documents(vector_store, question, k=8)
    if not search_results:
        return {"question": question, "answer": NO_ANSWER_MESSAGE, "sources": [], "context": ""}

    page_answers = []
    seen_pages = set()

    for doc in search_results:
        sentence, score = best_sentence_for_chunk(question, doc.page_content)
        if not sentence:
            continue
        source = doc.metadata.get("source", "Unknown")
        page = doc.metadata.get("page")
        key = (source, page)
        if key in seen_pages:
            continue
        seen_pages.add(key)
        page_answers.append({
            "source": source,
            "page": page,
            "answer": sentence[:900],
            "score": score,
            "label": source_label(doc),
        })

    if not page_answers:
        return {"question": question, "answer": NO_ANSWER_MESSAGE, "sources": [], "context": ""}

    page_answers.sort(key=lambda item: item["score"], reverse=True)
    best_score = page_answers[0]["score"]

    if best_score < 6:
        return {"question": question, "answer": NO_ANSWER_MESSAGE, "sources": [], "context": ""}

    # Keep strong matches only. If multiple pages are relevant, show them separately.
    strong_answers = [
        item for item in page_answers
        if item["score"] >= max(6, int(best_score * 0.65))
    ][:4]

    if len(strong_answers) == 1:
        answer_text = strong_answers[0]["answer"]
    else:
        sections = ["Relevant answers were found on multiple pages:"]
        for item in strong_answers:
            page_text = f"page {item['page']}" if item.get("page") else "page unknown"
            sections.append(f"**{item['source']} — {page_text}**\n\n{item['answer']}")
        answer_text = "\n\n---\n\n".join(sections)

    sources = [item["label"] for item in strong_answers]
    context = "\n\n".join([doc.page_content for doc in search_results])

    return {
        "question": question,
        "answer": answer_text,
        "sources": sources,
        "context": context,
        "page_answers": strong_answers,
    }
