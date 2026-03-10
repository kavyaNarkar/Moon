import os
import chromadb
from chromadb.config import Settings
import requests
from ..utils.logger import logger
from .document_processor import read_pdf, read_txt, read_docx

# Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db")
os.makedirs(DB_PATH, exist_ok=True)
COLLECTION_NAME = "moon_knowledge"
EMBED_MODEL = "mxbai-embed-large"

# Initialize ChromaDB
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_or_create_collection(name=COLLECTION_NAME)

def get_embedding(text):
    """Get embedding from local Ollama server."""
    try:
        response = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text}
        )
        return response.json()["embedding"]
    except Exception as e:
        logger.error(f"KNOWLEDGE: Embedding error: {e}")
        return None

def index_file(file_path):
    """Extracts text from a file and adds it to the vector database."""
    logger.info(f"KNOWLEDGE: Indexing {file_path}...")
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    
    try:
        if ext == ".pdf":
            text = read_pdf(file_path)
        elif ext == ".txt":
            text = read_txt(file_path)
        elif ext == ".docx":
            text = read_docx(file_path)
        else:
            logger.warning(f"KNOWLEDGE: Unsupported file type: {ext}")
            return False
            
        if not text:
            return False
            
        # Chunking (Simple for now: 1000 chars with overlap)
        chunk_size = 1000
        overlap = 200
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size - overlap)]
        
        for idx, chunk in enumerate(chunks):
            embedding = get_embedding(chunk)
            if embedding:
                collection.add(
                    embeddings=[embedding],
                    documents=[chunk],
                    ids=[f"{os.path.basename(file_path)}_{idx}"],
                    metadatas=[{"source": file_path}]
                )
        return True
    except Exception as e:
        logger.error(f"KNOWLEDGE: Failed to index {file_path}: {e}")
        return False

def search_knowledge(query, n_results=3):
    """Search the vector database for relevant context."""
    logger.info(f"KNOWLEDGE: Searching for '{query}'...")
    query_embedding = get_embedding(query)
    if not query_embedding:
        return []
        
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    return results["documents"][0]

def index_directory(directory_path):
    """Indexes all supported files in a directory."""
    count = 0
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith((".pdf", ".txt", ".docx")):
                if index_file(os.path.join(root, file)):
                    count += 1
    return count
