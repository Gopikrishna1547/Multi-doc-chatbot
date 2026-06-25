# Feature: PDF Loader Module

## Feature Branch
feature/pdf-loader

## Purpose
Handles all PDF loading and text extraction. Supports single PDF files, multiple PDFs, and Streamlit uploaded file objects.

## Functions

### load_pdf(filepath)
- Input: file path string
- Output: extracted text string
- Reads all pages and concatenates text

### load_multiple_pdfs(files)
- Input: list of Streamlit uploaded file objects
- Output: dictionary of filename to text
- Calls load_pdf_from_upload for each file

### load_pdf_from_upload(uploaded_file)
- Input: Streamlit uploaded file object
- Output: extracted text string
- Saves to temp file, extracts text, deletes temp file

## Dependencies
- pypdf
- tempfile (built-in)

## Error Handling
- Returns empty string if page has no extractable text
- Logs each file loaded with page count
