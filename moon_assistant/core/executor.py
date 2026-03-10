import os
import webbrowser
import subprocess
from ..config import APPLICATIONS, SEARCH_URL
from ..utils.logger import logger

def get_response_text(command):
    """
    Returns the text response for a given command.
    """
    task = command.get("task")
    
    if task == "open_application":
        app_name = command.get("application")
        return f"Opening {app_name}." if app_name else "Which application should I open?"
    
    elif task == "open_website":
        url = command.get("url", "")
        return f"Opening {url}." if url else "No URL provided."
    
    elif task == "search_web":
        query = command.get("query", "")
        return f"Searching for {query}." if query else "What should I search for?"
    
    elif task == "create_project":
        framework = command.get("framework", "react")
        name = command.get("name", "my-app")
        return f"Creating {framework} project {name}."
    
    elif task == "raagini":
        song = command.get("song")
        if song:
            return f"Playing {song} on Raagini."
        return "Opening your Raagini music player."
    
    elif task == "summarize_document":
        return "Processing the document for summary."
    
    elif task in ["chat", "welcome_message", "respond"]:
        return command.get("message", "I'm here to help!")
    
        return f"Sending WhatsApp message to {phone if phone else 'someone'}."

    elif task == "web_summarize":
        query = command.get("query", "")
        return f"Searching the web and summarizing information about {query}..."
        
    elif task == "web_news":
        topic = command.get("topic", "world news")
        return f"Fetching the latest news about {topic}..."

    elif task == "index_files":
        path = command.get("path", "")
        return f"Indexing files from {path} into my knowledge sphere..."
        
    elif task == "search_files":
        query = command.get("query", "")
        return f"Searching my knowledge sphere for '{query}'..."

    elif task == "system_stats":
        return "Checking your system performance metrics..."

    elif task == "help":
        return "Here is the help information."
    
    else:
        return f"I'm sorry, I don't know how to {task} yet."

def perform_action(command):
    """
    Performs the system action for a given command.
    """
    task = command.get("task")
    
    if task == "open_application":
        app_name = command.get("application")
        if app_name:
            open_application(app_name)
    
    elif task == "open_website":
        url = command.get("url")
        if url:
            open_website(url)
    
    elif task == "search_web":
        query = command.get("query")
        if query:
            search_web(query)
    
    elif task == "create_project":
        create_project(command)
    
    elif task == "raagini":
        from ..config import RAAGINI_PATH
        import subprocess
        song = command.get("song")
        try:
            if song:
                # Use shell=False (default) with a list of arguments
                # Quote the path if it has spaces, though subprocess usually handles this
                subprocess.Popen([RAAGINI_PATH, song])
            else:
                subprocess.Popen([RAAGINI_PATH])
        except Exception as e:
            logger.error(f"Failed to launch Raagini: {e}")
            return f"Error launching Raagini: {e}"
    
    elif task == "summarize_document":
        from ..tools.document_processor import summarize_document
        return summarize_document(command)

    elif task == "add_contact":
        from ..utils.database import add_contact
        return add_contact(command.get("name"), command.get("phone"))
    
    elif task == "list_contacts":
        from ..utils.database import list_contacts
        contacts = list_contacts()
        if not contacts:
            return "You have no saved contacts."
        return "Your contacts:\n" + "\n".join([f"- {name.capitalize()}: {phone}" for name, phone in contacts])

    elif task == "draft_whatsapp":
        from .brain import query_llm
        instruction = command.get("instruction", "a professional message")
        prompt = f"Draft a WhatsApp message based on this instruction: {instruction}. Output only the message text."
        draft = query_llm(prompt)
        return f"Here is a draft:\n\n\"{draft}\"\n\nWould you like me to send this? (Say 'send to [name]')"

    elif task == "broadcast_whatsapp":
        from ..tools.messenger import broadcast_whatsapp
        recipients = command.get("recipients", [])
        message = command.get("message", "")
        logger.info(f"EXECUTOR: Broadcasting WhatsApp message to {recipients}: '{message}'")
        return broadcast_whatsapp(recipients, message)

    elif task == "send_whatsapp":
        from ..tools.messenger import send_whatsapp_message, schedule_whatsapp_message
        from ..utils.database import get_contact
        import threading
        phone = command.get("phone", "")
        message = command.get("message", "")
        schedule_time = command.get("schedule_time", "")
        
        logger.info(f"EXECUTOR: WhatsApp Task - Phone: '{phone}', Message: '{message}'")
        
        # Pre-resolve contact name for better feedback
        display_target = phone
        if phone and not any(char.isdigit() for char in str(phone)):
            resolved = get_contact(phone.strip())
            if resolved:
                display_target = f"{phone} ({resolved})"
                logger.info(f"EXECUTOR: Resolved '{phone}' to '{resolved}'")
            else:
                logger.warning(f"EXECUTOR: Failed to resolve '{phone}'")
        
        if schedule_time:
            return schedule_whatsapp_message(phone, message, schedule_time)
            
        # Run in background to avoid GUI timeout
        threading.Thread(target=send_whatsapp_message, args=(phone, message)).start()
        return f"Starting WhatsApp process for {display_target}. Please keep the browser in focus."

    elif task == "web_summarize":
        from ..tools.web_intelligence import search_and_summarize
        return search_and_summarize(command.get("query", ""))
        
    elif task == "web_news":
        from ..tools.web_intelligence import get_latest_news
        return get_latest_news(command.get("topic", "world news"))
    elif task == "system_stats":
        import psutil
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()
        bat = psutil.sensors_battery()
        
        status = f"Your CPU is currently at {cpu} percent usage. "
        status += f"You are using {round(mem.used / (1024**3), 1)} GB of your {round(mem.total / (1024**3), 1)} GB RAM. "
        if bat:
            status += f"Battery is at {bat.percent} percent and is {'charging' if bat.power_plugged else 'discharging'}."
        else:
            status += "Battery information is unavailable."
        return status

    elif task == "index_files":
        from ..tools.knowledge_base import index_directory, index_file
        path = command.get("path", "")
        if os.path.isdir(path):
            count = index_directory(path)
            return f"Successfully indexed {count} files from {path}."
        elif os.path.isfile(path):
            if index_file(path):
                return f"Successfully indexed {path}."
            return f"Failed to index {path}. Unsupported format or unreadable."
        return f"Invalid path: {path}"
        
    elif task == "search_files":
        from ..tools.knowledge_base import search_knowledge
        from .brain import query_llm
        query = command.get("query", "")
        context_chunks = search_knowledge(query)
        
        if not context_chunks:
            return "I couldn't find any relevant information in your local files."
            
        combined_context = "\n\n".join(context_chunks)
        prompt = (
            f"You are Moon AI. Use the following context from the user's local files to answer their question. "
            f"If the answer isn't in the context, say you don't know based on the files provided.\n\n"
            f"Context:\n{combined_context}\n\nQuestion: {query}"
        )
        return query_llm(prompt)

def execute_task(command):
    """
    Routes the parsed command to the appropriate system action and returns a response.
    (Kept for backward compatibility)
    """
    response_text = get_response_text(command)
    action_result = perform_action(command)
    
    # If the action itself returns a final response (like summarize), use that.
    if action_result and isinstance(action_result, str):
        return action_result
        
    return response_text

def get_help_text():
    """Returns a string describing the available commands."""
    return (
        "\n--- Moon AI Assistant Help ---\n"
        "Here are some things you can ask me to do:\n\n"
        "1. Open Applications:\n"
        "   - 'open chrome'\n"
        "   - 'open vscode'\n"
        "   - 'open notepad'\n"
        "2. Open Websites:\n"
        "   - 'open youtube.com'\n"
        "   - 'open github'\n"
        "3. Web Search:\n"
        "   - 'search for latest AI news'\n"
        "   - 'search moon phase today'\n"
        "4. Development Tools:\n"
        "   - 'create a react project called website'\n"
        "   - 'create a flask app'\n"
        "5. Document Tools:\n"
        "   - 'summarize clipboard'\n"
        "   - 'summarize C:\\path\\to\\file.pdf'\n"
        "6. General Chat:\n"
        "   - 'hi', 'how are you?', 'what can you do?'\n"
        "   - Just talk to me!\n\n"
        "Type 'exit' or 'quit' to close the assistant.\n"
    )

def open_application(app_name):
    """Opens a system application."""
    if not app_name:
        return "Which application should I open?"
        
    # Mapping common names to Windows executable names or commands
    app_map = {
        "chrome": "start chrome",
        "browser": "start chrome",
        "code": "code",
        "vscode": "code",
        "vs code": "code",
        "notepad": "notepad",
        "calculator": "calc",
        "spotify": "start spotify",
        "terminal": "start powershell",
        "cmd": "start cmd"
    }
    
    cmd = app_map.get(app_name, app_name)
    logger.info(f"Opening application: {cmd}")
    
    try:
        # Use shell=True for 'start' commands
        subprocess.Popen(cmd, shell=True)
        return f"Opening {app_name}."
    except Exception as e:
        logger.error(f"Failed to open {app_name}: {e}")
        return f"Failed to open {app_name}. Make sure it is installed and in your PATH."

def open_website(url):
    """Opens a website in the default browser."""
    if not url:
        return "No URL provided."
    
    # Clean up common misconceptions in user input
    url = url.replace("link ", "").replace("website ", "").strip()
    
    # Ensure it's a proper URL
    if not url.startswith(("http://", "https://")):
        # If it looks like a domain (e.g., google.com), prepend https://
        if "." in url:
            url = "https://" + url
        else:
            # Otherwise, treat it as a search query
            return search_web(url)
            
    logger.info(f"Opening website: {url}")
    webbrowser.open(url)
    return f"Opening {url}."

def search_web(query):
    """Performs a web search."""
    if not query:
        return "What should I search for?"
        
    url = SEARCH_URL + query.replace(" ", "+")
    logger.info(f"Searching for: {query}")
    webbrowser.open(url)
    return f"Searching for {query}."

def create_project(command):
    """Sets up a development environment."""
    framework = command.get("framework", "react").lower()
    name = command.get("name", "my-app")
    
    logger.info(f"Creating {framework} project: {name}")
    
    try:
        if framework == "react":
            cmd = f"npm create vite@latest {name} -- --template react"
            subprocess.run(cmd, shell=True, check=True)
            return f"Created React project {name}."
        elif framework == "flask":
            os.makedirs(name, exist_ok=True)
            with open(os.path.join(name, "app.py"), "w") as f:
                f.write("from flask import Flask\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello Moon!'\n\nif __name__ == '__main__':\n    app.run(debug=True)")
            return f"Created Flask project {name}."
        else:
            return f"Framework {framework} is not supported yet."
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        return f"Error creating project: {e}"
