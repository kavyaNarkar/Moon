import os
import win32clipboard
from pypdf import PdfReader
from ..core.brain import query_llm
from ..utils.logger import logger

def get_clipboard_text():
    """Reads text from the Windows clipboard."""
    try:
        win32clipboard.OpenClipboard()
        data = win32clipboard.GetClipboardData()
        win32clipboard.CloseClipboard()
        return data
    except Exception as e:
        logger.error(f"Failed to read clipboard: {e}")
        return ""

def read_pdf(file_path):
    """Extracts text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"Failed to read PDF {file_path}: {e}")
        return ""

def read_txt(file_path):
    """Reads text from a plain text file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Failed to read TXT {file_path}: {e}")
        return ""

def summarize_document(command):
    """
    Extracts text from various sources and uses the LLM to summarize it.
    """
    source = command.get("source", "clipboard").lower()
    file_path = command.get("file_path", "")
    text = ""
    
    if source == "clipboard":
        text = get_clipboard_text()
    elif source == "txt" or (file_path and file_path.endswith(".txt")):
        text = read_txt(file_path)
    elif source == "pdf" or (file_path and file_path.endswith(".pdf")):
        text = read_pdf(file_path)
    elif source == "text":
        text = command.get("content", "")
    
    if not text:
        return f"I couldn't find any text to summarize from {source}."
        
    truncated_text = text[:4000]
    
    # Custom system prompt to ensure the LLM understands its only job is to summarize
    system_prompt = (
        "You are an expert document summarizer. "
        "Your goal is to provide a clear, concise summary of the provided text. "
        "Return your response in valid JSON format with a single key: 'summary'. "
        "JSON Example: {\"summary\": \"This document discusses...\"}"
    )
    
    summary_prompt = f"Please provide a concise summary of the following document:\n\n{truncated_text}"
    
    response = query_llm(summary_prompt, system_prompt=system_prompt)
    
    # Try 'summary' first, then fallback to 'message' then any string found
    return response.get("summary", response.get("message", "I processed the document, but failed to generate a summary."))
