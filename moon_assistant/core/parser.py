from ..utils.logger import logger

def quick_parse(text):
    """
    Attempts to parse common commands using regex/keywords before falling back to LLM.
    Returns a command dict if successful, else None.
    """
    text = text.lower().strip()
    
    # 0. Greetings & Help
    greetings = ["hi", "hello", "hey", "hola", "yo", "morning", "evening", "hii", "heyy"]
    chat_phrases = ["how are you", "how do you do", "who are you", "what's up", "sup", "how's it going"]
    creator_phrases = ["who created you", "who is your developer", "who made you", "who is your owner", "who built you"]
    
    # Check if the text matches exactly any greeting or starts with one + small text
    if any(text == g or text.startswith(g + " ") for g in greetings) and len(text) < 15:
        return {"task": "chat", "message": f"Hello! I'm Moon, your AI assistant. How can I help you today?"}
    
    if any(phrase in text for phrase in creator_phrases):
        from ..config import CREATOR_NAME
        return {"task": "chat", "message": f"I was created and developed by the talented {CREATOR_NAME}! He is my sole creator."}

    if any(phrase in text for phrase in chat_phrases):
        return {"task": "chat", "message": "I'm doing great, thank you for asking! I'm Moon, your local AI assistant. How can I help you today?"}
    
    if text in ["help", "?", "what can you do"]:
        return {"task": "help"}

    # 1. Open Application/Website
    if text.startswith("open "):
        target = text[5:].strip()
        
        # Check if it looks like a URL or a common web name
        common_sites = ["google", "github", "youtube", "facebook", "twitter", "reddit"]
        if "." in target or any(site in target for site in common_sites):
            return {"task": "open_website", "url": target}
        elif target == "raagini":
            return {"task": "raagini"}
        else:
            return {"task": "open_application", "application": target}

    # 1.5 Music Triggers (Raagini)
    music_keywords = ["play music", "play songs", "start music", "open raagini", "launch raagini", "play some music"]
    
    if any(text == kw for kw in music_keywords):
        return {"task": "raagini"}
    
    if text.startswith("play "):
        song = text[5:].strip()
        if song and song not in ["music", "songs", "some music"]:
            return {"task": "raagini", "song": song}
        return {"task": "raagini"}
            
    # 2. Search Web
    if text.startswith("search "):
        query = text[7:].strip()
        if query.startswith("for "):
            query = query[4:].strip()
        return {"task": "search_web", "query": query}
        
    # 3. Development Projects
    if "create" in text and ("project" in text or "app" in text):
        if "react" in text:
            name = text.split("called")[-1].strip() if "called" in text else "my-react-app"
            return {"task": "create_project", "framework": "react", "name": name}
        elif "flask" in text:
            return {"task": "create_project", "framework": "flask", "name": "my-flask-app"}
            
    return None

def parse_command(llm_json, original_text=""):
    """
    Parses the JSON output from the LLM and identifies the core task and parameters.
    """
    if not llm_json or "task" not in llm_json:
        logger.warning(f"Invalid command format: {llm_json}")
        return {"task": "unknown"}
    
    task_name = llm_json["task"]
    
    # STRICT GATE: Only allow summarize if the word is actually in the user text or implied
    if task_name == "summarize_document":
        text = original_text.lower()
        if not any(kw in text for kw in ["summarize", "summary", "doc", "text", "file", "clipboard", "read"]):
            logger.info("LLM suggested summarize but keyword not found. Falling back to chat.")
            return {"task": "chat", "message": llm_json.get("message", "I'm not sure if you wanted a summary. Could you clarify?")}
    
    logger.info(f"Parsed task: {task_name}")
    
    # Standardize parameters based on task type
    if task_name == "open_application":
        return {
            "task": "open_application",
            "application": llm_json.get("application", "").lower()
        }
    elif task_name == "open_website":
        return {
            "task": "open_website",
            "url": llm_json.get("url", "")
        }
    elif task_name == "search_web":
        return {
            "task": "search_web",
            "query": llm_json.get("query", "")
        }
    elif task_name == "create_project":
        return {
            "task": "create_project",
            "framework": llm_json.get("framework", "react"),
            "name": llm_json.get("name", "my-project")
        }
    elif task_name == "summarize_document":
        return {
            "task": "summarize_document",
            "source": llm_json.get("source", "clipboard"),
            "file_path": llm_json.get("file_path", "")
        }
    
    return llm_json
