import os

# Assistant Metadata
ASSISTANT_NAME = "Moon"
USER_NAME = "Kavya"
CREATOR_NAME = "Kavya"

# LLM Configuration
OLLAMA_MODEL = "phi3"
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Speech Configuration
VOSK_MODEL_PATH = os.path.join(os.getcwd(), "models", "vosk-model-small-en-us-0.15")
WAKE_WORD = "hello moon"

# Application Paths (Adjust as needed for Windows)
APPLICATIONS = {
    "vscode": "code",
    "chrome": "chrome",
    "spotify": "spotify",
    "notepad": "notepad"
}

# Brave Browser Paths
BRAVE_PATHS = [
    os.path.join(os.environ.get("PROGRAMFILES", "C:\\Program Files"), "BraveSoftware\\Brave-Browser\\Application\\brave.exe"),
    os.path.join(os.environ.get("PROGRAMFILES(X86)", "C:\\Program Files (x86)"), "BraveSoftware\\Brave-Browser\\Application\\brave.exe"),
    os.path.join(os.environ.get("LOCALAPPDATA", ""), "BraveSoftware\\Brave-Browser\\Application\\brave.exe")
]

# Raagini Music Player Path
RAAGINI_PATH = r"C:\Users\User\OneDrive\Apps\Raagini-v1\Raagini\build\windows\x64\runner\Release\raagini.exe"

# Web Search
SEARCH_URL = "https://www.google.com/search?q="

# Folders
BASE_DIR = os.getcwd()
TEMP_DIR = os.path.join(BASE_DIR, "temp")

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
