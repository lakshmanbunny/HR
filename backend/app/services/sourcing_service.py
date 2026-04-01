import httpx
import logging
from typing import List, Dict

# Configuration provided by the user
SERP_API_KEY = "632b7980bc9d929110133ee81ea024df4714e3342ee013efb164fdd9c043d28a"
BASE_URL = "https://serpapi.com/search"

logger = logging.getLogger(__name__)

def perform_search(query: str, target_count: int = 10) -> List[Dict]:
    """
    Performs Google Search via SerpApi and returns a list of candidate profiles.
    Pagination is handled to reach the target_count.
    """
    results = []
    start_index = 0 # SerpApi uses 0-based offset for 'start'
    
    try:
        while len(results) < target_count:
            params = {
                "api_key": SERP_API_KEY,
                "engine": "google",
                "q": query,
                "start": start_index,
                "num": 20 # Fetch 20 at a time for efficiency
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.get(BASE_URL, params=params)
                if response.status_code != 200:
                    logger.error(f"SerpApi Error {response.status_code}: {response.text}")
                response.raise_for_status()
                data = response.json()
            
            # SerpApi returns organic_results
            items = data.get("organic_results", [])
            if not items:
                break
                
            for item in items:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                    "displayLink": item.get("displayed_link")
                })
                if len(results) >= target_count:
                    break
            
            # Update start index for next page
            start_index += 20
            if start_index >= 200: # Increased limit to meet user's ~158 target
                break
                
    except Exception as e:
        logger.error(f"Error performing SerpApi Search: {str(e)}")
        # Return what we have so far
        pass
        
    return results
