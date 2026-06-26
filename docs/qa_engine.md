# Feature: QA Engine Module

## Feature Branch
feature/qa-engine

## Purpose
Handles all question answering logic. Takes a question and vector store, finds relevant context, and generates an accurate answer with source attribution.

## Functions

### get_qa_pipeline()
- Loads deepset/roberta-base-squad2 model
- Cached globally — loaded only once
- Returns Hugging Face QA pipeline

### build_context(search_results)
- Input: list of LangChain Document objects
- Output: tuple of context string and source list
- Joins all chunks into single context
- Extracts unique source document names

### generate_answer(question, context)
- Input: question string, context string
- Output: answer string
- Truncates context to 2000 characters for model limits
- Returns fallback message if answer not found

### ask_question(vector_store, question)
- Input: FAISS vector store, question string
- Output: dictionary with question, answer, sources, context
- Full pipeline: search + context + answer in one call

## Dependencies
- transformers
- torch
- src/vector_store.py
