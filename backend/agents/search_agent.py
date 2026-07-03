"""
Search Agent — uses Tavily to find relevant web sources for the research topic.
"""
from tools.web_search import search_web
from datetime import datetime

def run_search_agent(topic: str, domain: str = "general", num_queries: int = 3) -> list[dict]:
    """
    Generates multiple search queries for the topic and collects results.
    Returns a deduplicated list of search result dicts.
    """
    queries = _generate_queries(topic, domain)
    seen_urls = set()
    all_results = []

    for query in queries[:num_queries]:
        results = search_web(query, max_results=5)
        for r in results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                all_results.append(r)

    # Sort by relevance score
    all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
    return all_results[:12]  # top 12 unique sources


def _generate_queries(topic: str, domain: str) -> list[str]:
    """Create multiple search angles for a topic based on domain and current year."""
    year = datetime.now().year
    
    if domain == "healthcare":
        return [
            topic,
            f"{topic} medical research clinical trials {year}",
            f"{topic} efficacy guidelines safety consensus",
            f"{topic} systematic review meta-analysis",
        ]
    elif domain == "education":
        return [
            topic,
            f"{topic} educational research learning outcomes {year}",
            f"{topic} academic pedagogy study",
            f"{topic} curriculum impact analysis literature review",
        ]
    elif domain == "policy":
        return [
            topic,
            f"{topic} policy briefing paper {year}",
            f"{topic} government regulation analysis socioeconomic impact",
            f"{topic} policy feasibility study environmental assessment",
        ]
    elif domain == "science":
        return [
            topic,
            f"{topic} scientific paper breakthrough {year}",
            f"{topic} technical architecture methodology",
            f"{topic} peer-reviewed experimental findings",
        ]
    else:  # general
        return [
            topic,
            f"{topic} latest research {year}",
            f"{topic} key findings and insights",
            f"{topic} overview and analysis",
        ]
