"""
Research Agent — uses Groq LLM to summarize each search result into key points.
"""
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_groq_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not set in environment")
        _client = Groq(api_key=api_key)
    return _client


def run_research_agent(topic: str, search_results: list[dict], domain: str = "general") -> list[dict]:
    """
    For each search result, ask the LLM to extract key insights.
    Returns a list of {url, title, summary, key_points} dicts.
    """
    client = get_groq_client()
    summaries = []

    # Batch all sources into one prompt for efficiency
    sources_text = ""
    for i, r in enumerate(search_results[:8], 1):
        sources_text += f"\n[Source {i}] {r['title']}\nURL: {r['url']}\n{r['snippet']}\n"

    domain_guideline = ""
    if domain == "healthcare":
        domain_guideline = "Focus specifically on medical evidence, clinical trials, sample sizes, study validity, and patient health outcomes."
    elif domain == "education":
        domain_guideline = "Focus specifically on pedagogical methods, learning outcomes, classroom/demographic settings, sample sizes, and study impact."
    elif domain == "policy":
        domain_guideline = "Focus specifically on regulatory context, economic effects, societal stakeholders, policy feasibility, and environmental metrics."
    elif domain == "science":
        domain_guideline = "Focus specifically on core scientific foundations, experimental data, physical/digital methodology, and technology breakthroughs."
    else:
        domain_guideline = "Focus on extracting key factual assertions, evidence, and general conclusions."

    prompt = f"""You are a research analyst specializing in the {domain} domain. The user is researching: "{topic}"

Below are web sources collected about this topic. For EACH source, extract:
1. A 2-3 sentence summary
2. 2-4 bullet-point key facts or insights. {domain_guideline}

Format your response as a numbered list matching the source numbers.

SOURCES:
{sources_text}

Respond in this format for each source:
[Source N]
Summary: ...
Key Points:
- ...
- ...
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000,
    )

    raw = response.choices[0].message.content
    summaries = _parse_summaries(raw, search_results)
    return summaries


def _parse_summaries(raw_text: str, search_results: list[dict]) -> list[dict]:
    """Parse the LLM response and attach to original source metadata."""
    summaries = []
    blocks = raw_text.split("[Source ")
    for i, block in enumerate(blocks[1:], 1):
        if i <= len(search_results):
            src = search_results[i - 1]
            summaries.append({
                "title": src["title"],
                "url": src["url"],
                "snippet": src["snippet"],
                "llm_analysis": block.strip(),
            })
    return summaries
