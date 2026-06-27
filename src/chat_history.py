import logging
from datetime import datetime

log = logging.getLogger(__name__)


def format_chat_history(chat_history: list) -> str:
    """Format chat history as readable text string."""
    log.info("Formatting chat history")
    if not chat_history:
        return "No conversation history yet."
    lines = []
    for message in chat_history:
        role = "You" if message["role"] == "user" else "Assistant"
        lines.append(f"{role}: {message['content']}")
        if message["role"] == "assistant" and "sources" in message:
            if message["sources"]:
                lines.append(f"Sources: {', '.join(message['sources'])}")
        lines.append("")
    return "\n".join(lines)
