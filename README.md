# 📄 Multi-Document AI Assistant

A Streamlit-based Retrieval-Augmented Generation (RAG) style chatbot that allows users to upload multiple PDF documents, generate a short summary, review important questions, and ask questions that are answered only from the uploaded PDF content.

---

## 🚀 Features

- 📂 Upload one or more PDF documents
- 📄 Generate a concise **5-10 point PDF summary**
- ❓ Generate **document-specific important questions and answers**
- 💬 Ask custom questions about uploaded PDFs
- 🎯 Return only **one best answer** from the most relevant document content
- 🚫 Show a clear fallback message when an answer is not available in the PDFs
- 📌 Display source PDF name and page number where available
- 📊 Show document statistics such as PDFs, pages, chunks, and questions asked
- ✅ Unit tested with Pytest

Fallback message:

```text
I could not find an answer to this question in the uploaded PDF document(s).
```

---

## 🏗️ Application Workflow

```text
User uploads PDFs
        │
        ▼
PDF text extraction with page markers
        │
        ▼
Text chunking with source + page metadata
        │
        ▼
FAISS vector store creation
        │
        ├──► Short PDF summary
        ├──► Important Q&A generation
        └──► User question answering
                    │
                    ▼
            One best PDF-grounded answer
```

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core programming language |
| Streamlit | Web interface |
| LangChain Community | Embeddings and FAISS integration |
| FAISS | Vector similarity search |
| Sentence Transformers | Text embeddings |
| PyPDF2 | PDF text extraction |
| Pytest | Unit testing |

---

## 📂 Project Structure

```text
Multi-doc-chatbot/
├── app.py
├── requirements.txt
├── README.md
├── conftest.py
├── src/
│   ├── pdf_loader.py
│   ├── vector_store.py
│   ├── qa_engine.py
│   └── chat_history.py
├── tests/
│   └── test_main.py
└── docs/
```

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/Gopikrishna1547/Multi-doc-chatbot.git
cd Multi-doc-chatbot
```

### 2. Create a virtual environment

macOS / Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

Open the browser at:

```text
http://localhost:8501
```

---

## 🧪 Run Tests

```bash
python3 -m pytest tests/test_main.py -v
```

Expected result:

```text
7 passed
```

---

## 💡 Example Questions

For a COVID-19 PDF:

- What virus caused COVID-19?
- How did COVID-19 affect mental health?
- What does the document say about the Omicron variant?
- Why is vaccination important according to the document?
- What public health measures are recommended to reduce COVID-19 spread?

For a population PDF:

- What does the document explain about population growth?
- How many people are born and die each year worldwide?
- What is the demographic transition?
- How does fertility affect population growth?

---

## 🌿 Git Workflow

Recommended development workflow:

```bash
git checkout dev
# make changes
git add .
git commit -m "Meaningful commit message"
git push origin dev
```

Then create a Pull Request:

```text
base: main
compare: dev
```

---

## 🔮 Future Improvements

- Add support for DOCX and TXT files
- Add OCR support for scanned PDFs
- Use an LLM for more natural summaries and answers
- Add highlighted source text
- Export summary and generated Q&A to PDF
- Add user authentication

---

## 👨‍💻 Author

**Gopikrishna Bojedla**

- GitHub: https://github.com/Gopikrishna1547
