# Feature: Vector Store Module

## Feature Branch
feature/vector-store

## Purpose
Handles all vector store operations. Converts document text into vector embeddings and stores them in FAISS for fast similarity search.

## Functions

### get_embeddings()
- Loads sentence-transformers/all-MiniLM-L6-v2 model
- Returns HuggingFaceEmbeddings object
- Model loaded once and reused

### split_text(text, source_name)
- Input: raw text string, document name
- Output: list of LangChain Document chunks
- Each chunk tagged with source document name in metadata
- Chunk size: 500 characters, overlap: 50

### build_vector_store(documents)
- Input: dictionary of filename to text
- Output: FAISS vector store object
- Splits all documents into chunks
- Builds combined vector store from all chunks

### search_documents(vector_store, query, k)
- Input: vector store, query string, number of results
- Output: list of most relevant document chunks
- Each result includes source document name in metadata

## Dependencies
- langchain-community
- langchain-text-splitters
- sentence-transformers
- faiss-cpu
