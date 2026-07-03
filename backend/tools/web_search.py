import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_tavily_client() -> TavilyClient:
    global _client
    if _client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not set in environment")
        _client = TavilyClient(api_key=api_key)
    return _client

def search_web(query: str, max_results: int = 6) -> list[dict]:
    """
    Search the web using Tavily and return a list of results.
    Each result has: title, url, content (snippet), score.
    """
    client = get_tavily_client()
    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
        include_raw_content=False,
    )
    results = []
    for r in response.get("results", []):
        results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "snippet": r.get("content", ""),
            "score": r.get("score", 0.0),
        })
    return results
