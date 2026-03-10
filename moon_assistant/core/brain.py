import requests
import json
from ..config import OLLAMA_MODEL, OLLAMA_API_URL
from ..utils.logger import logger

def query_llm(prompt, system_prompt=None):
    """
    Sends a prompt to the local Ollama LLM with minimal overhead and reliable JSON output.
    """
    logger.debug(f"Querying LLM: {prompt}")
    
    if system_prompt is None:
        from ..config import CREATOR_NAME
        system_prompt = (
            f"You are Moon, a premium local AI assistant created by {CREATOR_NAME}. "
            "Return valid JSON for the user's intent. "
            "TASKS:\n"
            "- 'system_stats': For CPU, RAM, or Battery queries.\n"
            "- 'web_summarize': For complex questions, research, or 'what is/who is' queries requiring web data.\n"
            "- 'web_news': For latest news or current events.\n"
            "- 'search_files': For questions about the user's documents/personal files (Local RAG).\n"
            "- 'index_files': For requests to 'learn' or 'read' a folder/directory.\n"
            "- 'open_application' / 'open_website' / 'search_web': Basic system automation.\n"
            "- 'chat': For general talk, greetings, or when no other task fits.\n"
            "CRITICAL: Always return JSON: {\"task\": \"TASK_NAME\", \"message\": \"MESSAG_TEXT\", \"query/path/url\": \"PARAMS\"}"
        )
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"{system_prompt}\n\nUser: {prompt}",
        "stream": False,
        "format": "json"
    }
    
    try:
        # 120s timeout for local processing on iGPU
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        response_text = result.get("response", "").strip()
        logger.debug(f"LLM Response text: {response_text}")
        
        try:
            # Clean up potential markdown formatting from LLM
            clean_text = response_text
            if "```json" in clean_text:
                clean_text = clean_text.split("```json")[-1].split("```")[0].strip()
            elif "```" in clean_text:
                clean_text = clean_text.split("```")[-1].split("```")[0].strip()
            
            return json.loads(clean_text)
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse LLM JSON: {response_text}")
            return {"task": "chat", "message": response_text}
            
    except Exception as e:
        logger.error(f"Error querying Ollama: {str(e)}")
        return {"task": "unknown", "error": str(e)}
