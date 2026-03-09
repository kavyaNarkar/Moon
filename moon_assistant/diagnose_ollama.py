import requests
import sys

def check_ollama():
    url = "http://localhost:11434/api/tags"
    print("--- Moon Diagnostic Tool ---")
    print(f"Checking Ollama server at {url}...")
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("[SUCCESS] Ollama is running.")
            models = [m['name'] for m in response.json().get('models', [])]
            print(f"Available models: {', '.join(models)}")
            if 'phi3:latest' in models or 'phi3' in models:
                print("[SUCCESS] 'phi3' model is installed.")
            else:
                print("[WARNING] 'phi3' model NOT found. Run: ollama pull phi3")
        else:
            print(f"[ERROR] Ollama returned status code: {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Ollama is NOT reachable. Ensure Ollama is running.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    check_ollama()
