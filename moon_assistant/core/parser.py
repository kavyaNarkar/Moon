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
    
    # 4. WhatsApp Messaging
    whatsapp_variants = ["whatsapp", "whatssapp", "watsapp", "watsap", "messenger"]
    if any(v in text for v in whatsapp_variants):
        import re
        import dateparser
        
        # Check for contact management
        if "save" in text or "add" in text:
            match = re.search(r'(?:save|add) (.*?) (?:with|as) (\d{10,15})', text)
            if match:
                return {"task": "add_contact", "name": match.group(1).strip(), "phone": match.group(2)}
        
        if "list" in text and "contact" in text:
            return {"task": "list_contacts"}

        # Check for AI Drafting
        if "draft" in text:
            return {"task": "draft_whatsapp", "instruction": text.replace("draft", "").replace("whatsapp", "").strip()}

        # Bulletproof WhatsApp Extraction
        phone = ""
        message = ""
        schedule_time = ""
        
        # 1. Target (Name or Phone)
        # Look for "to [Target]"
        to_match = re.search(r'\bto\b\s+(?:\[|")?([a-zA-Z0-9]+)(?:\]|")?', text, re.IGNORECASE)
        if to_match:
            phone = to_match.group(1).strip()
        else:
            # Fallback: look for 10-digit number
            num_match = re.search(r'(\d{10,15})', text)
            if num_match:
                phone = num_match.group(1)
            else:
                # Fallback: name after 'send' or 'message'
                name_match = re.search(r'(?:send|message)(?:\s+whatsapp)?\s+(?:to\s+)?([a-zA-Z]+)', text, re.IGNORECASE)
                if name_match and name_match.group(1).lower() not in whatsapp_variants:
                    phone = name_match.group(1).strip()

        # 2. Message Content
        # Priority: literal quotes/brackets
        quote_match = re.search(r'["\'\[](.*?)["\'\]]', text)
        if quote_match:
            message = quote_match.group(1).strip()
        else:
            # Take everything that isn't the phone or keywords
            clean_text = text
            if phone: clean_text = clean_text.replace(phone.lower(), "", 1)
            for v in whatsapp_variants + ["send", "to", "message", "whatsapp", "at"]:
                clean_text = re.sub(rf'\b{v}\b', '', clean_text, flags=re.IGNORECASE)
            message = clean_text.strip()

        # 3. Schedule Time
        time_parts = text.split("at")
        if len(time_parts) > 1:
            possible_time = time_parts[-1].strip()
            parsed = dateparser.parse(possible_time, settings={'PREFER_DATES_FROM': 'future'})
            if parsed:
                schedule_time = possible_time
                # Remove time from message if it leaked in
                message = message.replace(f"at {possible_time}", "").replace(possible_time, "").strip()

        if "broadcast" in text:
            recipients = re.findall(r'(\d{10,15})', text)
            return {"task": "broadcast_whatsapp", "recipients": recipients, "message": message}
            
        if phone or message:
            logger.info(f"PARSER: Extracted WhatsApp -> Target: '{phone}', Message: '{message}', Sched: '{schedule_time}'")
            return {
                "task": "send_whatsapp", 
                "phone": phone, 
                "message": message,
                "schedule_time": schedule_time
            }
            
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
    elif task_name == "send_whatsapp":
        return {
            "task": "send_whatsapp",
            "phone": llm_json.get("phone", ""),
            "message": llm_json.get("message", "")
        }
    
    return llm_json
