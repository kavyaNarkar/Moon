import requests
from bs4 import BeautifulSoup
from googlesearch import search
from ..core.brain import query_llm
from ..utils.logger import logger

def search_and_summarize(query, num_results=3):
    """
    Searches Google for a query, scrapes the top results, and returns an AI summary.
    """
    logger.info(f"WEB_INTEL: Searching for '{query}'...")
    try:
        results = []
        # Get top links
        links = list(search(query, num_results=num_results))
        
        for link in links:
            try:
                logger.info(f"WEB_INTEL: Scraping {link}...")
                response = requests.get(link, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    # Extract text from paragraphs
                    paragraphs = soup.find_all('p')
                    text = ' '.join([p.get_text() for p in paragraphs[:5]]) # Take first 5 paragraphs
                    if len(text) > 100:
                        results.append(f"Source: {link}\nContent: {text}")
            except Exception as e:
                logger.warning(f"WEB_INTEL: Failed to scrape {link}: {e}")
                
        if not results:
            return "I searched the web but couldn't find readable content to summarize."
            
        combined_text = "\n\n".join(results)[:5000] # Limit context for LLM
        
        system_prompt = (
            "You are Moon's Web Intelligence engine. "
            "Summarize the provided search results into a concise, informative brief. "
            "Focus on answering the user's original query directly. "
            "Return your response in valid JSON format with a single key: 'summary'."
        )
        
        prompt = f"User Query: {query}\n\nSearch Results:\n{combined_text}"
        
        logger.info("WEB_INTEL: Querying LLM for summary...")
        ai_response = query_llm(prompt, system_prompt=system_prompt)
        
        return ai_response.get("summary", "I found some information but couldn't summarize it properly.")
        
    except Exception as e:
        logger.error(f"WEB_INTEL: Global error in search_and_summarize: {e}")
        return f"I encountered an error while searching the web: {str(e)}"

def get_latest_news(topic="world news"):
    """Fetch and summarize latest news for a specific topic."""
    query = f"latest {topic}"
    return search_and_summarize(query, num_results=5)
