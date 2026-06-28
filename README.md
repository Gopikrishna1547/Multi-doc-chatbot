# Multi-Document AI Assistant

A Streamlit-based PDF assistant that lets users upload multiple PDF documents, generate document-wise summaries, generate document-wise questions, and ask questions that are answered only from the uploaded PDFs.

## Features

- Upload up to 5 PDF documents.
- Extract readable text from uploaded PDFs.
- Build a searchable vector index with FAISS.
- Generate a separate 5-7 line summary for each document.
- Generate important questions and answers for each document.
- Answer user questions using only uploaded PDF content.
- Return source PDF names and page numbers.
- Show multiple page-based answers when relevant information appears on more than one page.
- Show a fallback message when the answer is not found in the uploaded PDFs.
- Display document statistics such as document count, page count, chunk count, and question count.

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Core language |
| Streamlit | Web interface |
| PyPDF / PyPDF2 | PDF text extraction |
| LangChain | Document processing and vector workflow |
| FAISS | Vector search |
| Hugging Face Sentence Transformers | Embeddings |
| Pytest | Unit testing |

## Project Structure

```text
Multi-doc-chatbot/
├── app.py
├── requirements.txt
├── README.md
├── src/
│   ├── pdf_loader.py
│   ├── vector_store.py
│   ├── qa_engine.py
│   └── chat_history.py
├── tests/
│   └── test_main.py
└── docs/
```

## Setup

Clone the repository:

```bash
git clone https://github.com/Gopikrishna1547/Multi-doc-chatbot.git
cd Multi-doc-chatbot
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

## Usage

1. Open the Streamlit app.
2. Upload up to 5 PDF documents from the sidebar.
3. Click **Process Documents**.
4. Review the summary for each document.
5. Review the generated questions for each document.
6. Ask your own questions in the chat box.
7. Check the answer and source page references.

## Testing

Run the test suite:

```bash
python3 -m pytest tests/test_main.py -v
```

## Answering Behavior

The assistant searches uploaded PDFs and returns answers only from retrieved PDF content. If matching content appears on multiple pages, the answer is grouped by page. If no strong matching content is found, the assistant returns:

```text
I could not find an answer to this question in the uploaded PDF document(s).
```

## Notes

- Works best with text-based PDFs.
- Scanned image-only PDFs may require OCR before upload.
- The app does not answer from outside knowledge.
