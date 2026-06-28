import logging
import re
from collections import Counter

log = logging.getLogger(__name__)

NO_ANSWER_MESSAGE = "I could not find an answer to this question in the uploaded PDF document(s)."

STOP_WORDS = {
    "the", "is", "are", "was", "were", "a", "an", "and", "or", "to",
    "of", "in", "on", "for", "with", "what", "when", "where", "why",
    "how", "many", "much", "does", "do", "did", "by", "from", "this",
    "that", "it", "as", "at", "be", "has", "have", "had", "about"
}


def build_context(search_results: list) -> tuple:
    context = "\n\n".join([doc.page_content for doc in search_results])
    sources = list(set([
        doc.metadata.get("source", "Unknown")
        for doc in search_results
    ]))
    return context, sources


def split_sentences(text: str) -> list:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 40]


def clean_words(text: str) -> set:
    words = set(re.findall(r"\w+", text.lower()))
    return {w for w in words if w not in STOP_WORDS and len(w) > 2}


def score_sentence(question: str, sentence: str) -> int:
    question_words = clean_words(question)
    sentence_words = clean_words(sentence)

    score = len(question_words & sentence_words)

    question_lower = question.lower()
    sentence_lower = sentence.lower()

    if "virus" in question_lower and ("sars" in sentence_lower or "coronavirus" in sentence_lower):
        score += 4

    if "covid" in question_lower and "covid" in sentence_lower:
        score += 3

    if "mental" in question_lower and "mental health" in sentence_lower:
        score += 4

    if "omicron" in question_lower and "omicron" in sentence_lower:
        score += 4

    if "delta" in question_lower and "delta" in sentence_lower:
        score += 4

    if "vaccination" in question_lower or "vaccine" in question_lower:
        if "vaccination" in sentence_lower or "vaccine" in sentence_lower or "vaccinated" in sentence_lower:
            score += 4

    if "recommend" in question_lower and ("recommend" in sentence_lower or "recommends" in sentence_lower):
        score += 3

    return score


def generate_answer(question: str, context: str) -> str:
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

    if best_score < 2:
        return NO_ANSWER_MESSAGE

    return best_sentence[:700]


def summarize_documents(documents: dict) -> str:
    """Generate a short 5-10 point summary from uploaded PDFs."""
    all_text = " ".join(documents.values())
    sentences = split_sentences(all_text)

    if not sentences:
        return "Summary could not be generated because no readable text was found."

    keywords = [
        "objective", "pandemic", "covid", "virus", "variant", "vaccination",
        "population", "growth", "death", "birth", "recommend", "important",
        "result", "conclusion", "health", "mental", "who", "paho", "delta",
        "omicron", "sars", "coronavirus"
    ]

    scored = []
    seen = set()

    for sentence in sentences:
        lower_sentence = sentence.lower()
        score = sum(1 for word in keywords if word in lower_sentence)

        normalized = lower_sentence[:120]
        if score > 0 and normalized not in seen:
            scored.append((score, sentence))
            seen.add(normalized)

    selected = [sentence for _, sentence in sorted(scored, reverse=True)[:7]]

    if not selected:
        selected = sentences[:5]

    return "\n".join([f"- {sentence[:350]}" for sentence in selected])


def make_question_from_sentence(sentence: str) -> str:
    lower = sentence.lower()

    if "sars-cov-2" in lower or "coronavirus" in lower:
        return "What virus caused COVID-19?"

    if "mental health" in lower or "psychosocial" in lower:
        return "How did COVID-19 affect mental health?"

    if "omicron" in lower:
        return "What does the document say about the Omicron variant?"

    if "delta" in lower:
        return "What does the document say about the Delta variant?"

    if "vaccination" in lower or "vaccines" in lower or "vaccinated" in lower:
        return "Why is vaccination important according to the document?"

    if "world health organization" in lower or "who" in lower:
        return "What does WHO recommend according to the document?"

    if "mask" in lower or "distance" in lower or "hands clean" in lower:
        return "What public health measures are recommended to reduce COVID-19 spread?"

    if "population growth" in lower:
        return "What does the document explain about population growth?"

    if "birth" in lower and "death" in lower:
        return "How do births and deaths affect population growth?"

    return "What important information does this part of the document explain?"


def generate_important_qa(documents: dict) -> list:
    """Generate document-specific important questions and answers."""
    all_text = " ".join(documents.values())
    sentences = split_sentences(all_text)

    if not sentences:
        return []

    important_keywords = [
        "covid", "sars-cov-2", "coronavirus", "pandemic", "variant",
        "omicron", "delta", "vaccination", "vaccine", "mental health",
        "who", "recommend", "public health", "population growth",
        "birth", "death", "demographic"
    ]

    candidates = []
    for sentence in sentences:
        lower = sentence.lower()
        score = sum(1 for keyword in important_keywords if keyword in lower)
        if score > 0:
            candidates.append((score, sentence))

    if not candidates:
        candidates = [(1, sentence) for sentence in sentences[:7]]

    qa_pairs = []
    used_questions = set()

    for _, sentence in sorted(candidates, reverse=True):
        question = make_question_from_sentence(sentence)

        if question not in used_questions:
            qa_pairs.append({
                "question": question,
                "answer": sentence[:700]
            })
            used_questions.add(question)

        if len(qa_pairs) >= 7:
            break

    return qa_pairs


def ask_question(vector_store, question: str) -> dict:
    from src.vector_store import search_documents

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
