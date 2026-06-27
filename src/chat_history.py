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


def save_chat_as_pdf(chat_history: list, topic: str = "Chat") -> str:
    """Save chat history as a formatted PDF file."""
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib import colors
    import os

    os.makedirs("reports", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"reports/chat_{timestamp}.pdf"

    doc = SimpleDocTemplate(filename, pagesize=A4,
        leftMargin=20*2.835, rightMargin=20*2.835,
        topMargin=20*2.835, bottomMargin=20*2.835)

    title_style = ParagraphStyle("title", fontSize=16,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1F4E79"), spaceAfter=8)
    user_style = ParagraphStyle("user", fontSize=10,
        fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2E75B6"), spaceAfter=4)
    assistant_style = ParagraphStyle("assistant", fontSize=10,
        fontName="Helvetica",
        textColor=colors.HexColor("#595959"), spaceAfter=4)
    source_style = ParagraphStyle("source", fontSize=8,
        fontName="Helvetica",
        textColor=colors.gray, spaceAfter=8)

    story = []
    story.append(Paragraph("Multi-Document Chatbot — Chat History", title_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        source_style
    ))
    story.append(HRFlowable(width="100%", thickness=0.8,
        color=colors.HexColor("#2E75B6"), spaceAfter=12))

    for message in chat_history:
        if message["role"] == "user":
            story.append(Paragraph(f"You: {message['content']}", user_style))
        else:
            story.append(Paragraph(f"Assistant: {message['content']}", assistant_style))
            if "sources" in message and message["sources"]:
                story.append(Paragraph(
                    f"Sources: {', '.join(message['sources'])}",
                    source_style
                ))
        story.append(Spacer(1, 6))

    doc.build(story)
    log.info(f"Chat history saved to: {filename}")
    return filename
