"""
Report Agent — generates the final structured research report with citations.
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



def run_report_agent(topic: str, verified_facts: dict, summaries: list[dict], domain: str = "general") -> dict:
    """
    Generates a full markdown research report with citations.
    Returns: { markdown: str, citations: list[dict] }
    """
    client = get_groq_client()

    facts_text = "\n".join(f"- {f}" for f in verified_facts.get("verified_facts", []))
    uncertain_text = "\n".join(f"- {f}" for f in verified_facts.get("uncertain_claims", []))
    consensus = verified_facts.get("consensus", "")

    sources_text = ""
    for i, s in enumerate(summaries[:8], 1):
        sources_text += f"[{i}] {s['title']} — {s['url']}\n"

    # Set up custom headers depending on domain
    if domain == "healthcare":
        headers = """## Executive Summary
## Introduction
## Clinical & Evidence Overview
## Study Methods & Limitations
## Healthcare Implications
## Areas of Uncertainty
## Conclusion"""
    elif domain == "education":
        headers = """## Executive Summary
## Introduction
## Pedagogical Context
## Methodological Quality
## Educational Outcomes
## Areas of Uncertainty
## Conclusion"""
    elif domain == "policy":
        headers = """## Executive Summary
## Introduction
## Policy & Regulatory Context
## Stakeholder & Economic Impact
## Implementation Feasibility
## Areas of Uncertainty
## Conclusion"""
    elif domain == "science":
        headers = """## Executive Summary
## Introduction
## Scientific & Technical Foundations
## Experimental Evidence
## Technological Innovations & Future Work
## Areas of Uncertainty
## Conclusion"""
    else:
        headers = """## Executive Summary
## Introduction
## Key Findings
## Detailed Analysis
## Areas of Uncertainty
## Conclusion"""

    prompt = f"""You are an expert research writer specializing in the {domain} domain. Write a comprehensive, well-structured research report on: "{topic}"

Use the following verified information:

CONSENSUS:
{consensus}

VERIFIED FACTS:
{facts_text}

AREAS OF UNCERTAINTY:
{uncertain_text}

SOURCES AVAILABLE:
{sources_text}

Write a detailed report in Markdown format with exactly these sections:
{headers}

Rules:
- Use **bold** for important terms
- Add [N] citation markers where facts come from numbered sources
- Be thorough but clear — aim for 600-900 words
- Do NOT make up facts not present in the verified information
- Write in a professional, academic tone
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=3000,
    )

    markdown = response.choices[0].message.content

    # Build citations list from summaries
    citations = [
        {
            "title": s["title"],
            "url": s["url"],
            "snippet": s.get("snippet", "")[:200],
        }
        for s in summaries[:8]
    ]

    return {
        "markdown": markdown,
        "citations": citations,
    }
