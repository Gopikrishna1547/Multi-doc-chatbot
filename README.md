# 📄 Multi-Document Chatbot

A Retrieval-Augmented Generation (RAG) chatbot built with **Python**, **Streamlit**, **LangChain**, and **FAISS**. This application allows users to upload multiple PDF documents and ask questions based only on the uploaded content.

---

# 🚀 Features

* 📚 Upload up to **5 PDF documents**
* 🔍 Semantic search across multiple PDFs
* 🤖 AI-powered question answering
* ⚡ Fast document retrieval using FAISS
* 📄 Displays the source document
* 💬 Maintains chat history
* 🧹 Clear chat history
* 📥 Download chat history
* ✅ Unit tested with Pytest

---

# 🏗️ Architecture

```text
User Uploads PDFs
        │
        ▼
PDF Text Extraction
        │
        ▼
Text Chunking
        │
        ▼
Sentence Embeddings
        │
        ▼
FAISS Vector Database
        │
        ▼
Similarity Search
        │
        ▼
LangChain QA Engine
        │
        ▼
Answer + Source Document
```

---

# 🛠️ Tech Stack

| Technology            | Purpose                        |
| --------------------- | ------------------------------ |
| Python                | Programming Language           |
| Streamlit             | Web Application                |
| LangChain             | Retrieval-Augmented Generation |
| FAISS                 | Vector Database                |
| Sentence Transformers | Text Embeddings                |
| PyPDF2                | PDF Text Extraction            |
| Pytest                | Unit Testing                   |

---

# 📂 Project Structure

```text
multi-doc-chatbot/
│
├── src/
│   ├── pdf_loader.py
│   ├── vector_store.py
│   ├── qa_engine.py
│   ├── chat_history.py
│
├── tests/
│   └── test_main.py
│
├── docs/
│
├── app.py
├── requirements.txt
├── README.md
└── conftest.py
```

---

# ⚙️ Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/Gopikrishna1547/Multi-doc-chatbot.git

cd Multi-doc-chatbot
```

---

## 2️⃣ Create a Virtual Environment (Recommended)

### macOS / Linux

```bash
python3 -m venv venv

source venv/bin/activate
```

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Run the Application

```bash
streamlit run app.py
```

Open your browser:

```text
http://localhost:8501
```

---

## 5️⃣ Using the Chatbot

1. Upload one or more PDF documents.
2. Click **Process Documents**.
3. Wait for processing to finish.
4. Ask questions related to the uploaded PDFs.
5. View the generated answer and source document.
6. Download or clear the chat history if required.

---

# 🧪 Running Tests

Run all unit tests:

```bash
python3 -m pytest tests/test_main.py -v
```

Expected output:

```text
========================
7 passed
========================
```

---

# 💡 Example Questions

* What is the population of India?
* Which iPhone model was released in 2020?
* Summarize this document.
* Which document contains information about demographic transition?
* Compare the information from two uploaded PDFs.

---

# 🔮 Future Improvements

* Support DOCX and TXT files
* Page-level citations
* Conversation memory
* Cloud vector database
* User authentication
* Support additional LLM providers

---

# 🌿 Git Workflow

This project follows a simple Git workflow:

* **main** → Stable production-ready code
* **dev** → Active development and feature integration

All new features are developed and tested in the **dev** branch before being merged into **main**.

---

# 👨‍💻 Author

**Gopikrishna Bojedla**

* GitHub: https://github.com/Gopikrishna1547
* LinkedIn: *(Add your LinkedIn profile URL here)*

---

## ⭐ If you found this project useful, consider giving it a star on GitHub!

