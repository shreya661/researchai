"""
Fact-Check Agent — verifies and filters information from the research summaries.
Removes contradictions, flags uncertain claims, and consolidates verified facts.
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



def run_factcheck_agent(topic: str, summaries: list[dict], domain: str = "general") -> dict:
    """
    Takes research summaries and returns verified facts + flagged uncertainties.
    Returns: { verified_facts: [...], uncertain_claims: [...], consensus: str }
    """
    client = get_groq_client()

    combined = ""
    for i, s in enumerate(summaries, 1):
        combined += f"\n[Source {i}] {s['title']}\n{s['llm_analysis']}\n"

    domain_guideline = ""
    if domain == "healthcare":
        domain_guideline = "For verification, heavily prioritize findings backed by rigorous studies, clinical trials, and healthcare consensus. Mark anecdotal stories, opinion pieces, or small-scale pilot claims as uncertain."
    elif domain == "education":
        domain_guideline = "Prioritize educational consensus, peer-reviewed pedagogical studies, and large-scale experimental cohorts. Tag isolated classroom anecdotes or unsupported product/software marketing claims as uncertain."
    elif domain == "policy":
        domain_guideline = "Cross-verify legislative facts and economic stats. Flag partisan reports, non-peer-reviewed white papers, and speculative policy impacts as uncertain. Call out contradictions in projections."
    elif domain == "science":
        domain_guideline = "Prioritize peer-reviewed breakthroughs, empirical experimental data, and mathematical/computational consensus. Flag non-replicated claims or generic technology vendor claims as uncertain."
    else:
        domain_guideline = "Cross-reference facts appearing in multiple sources. Flag isolated, uncorroborated, or anecdotal claims as uncertain."

    prompt = f"""You are a fact-checking expert specializing in the {domain} domain. The research topic is: "{topic}"

Below are summaries and analyses from multiple web sources. Your job is to:
1. Identify facts that appear in MULTIPLE sources (high confidence)
2. Identify claims that appear in only ONE source (uncertain/unverified)
3. Identify any contradictions between sources
4. Write a brief consensus statement about what is most reliably known

{domain_guideline}

RESEARCH SUMMARIES:
{combined}

Respond in this EXACT format:

VERIFIED FACTS:
- [fact supported by multiple sources]
- [fact supported by multiple sources]

UNCERTAIN CLAIMS:
- [claim from only one source]

CONTRADICTIONS:
- [contradiction if any, or "None found"]

CONSENSUS:
[2-3 sentence statement of what is reliably established about this topic]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content
    return _parse_factcheck(raw)


def _parse_factcheck(raw: str) -> dict:
    """Parse the structured fact-check response."""
    result = {
        "verified_facts": [],
        "uncertain_claims": [],
        "contradictions": [],
        "consensus": "",
    }

    section = None
    for line in raw.split("\n"):
        line = line.strip()
        if line.startswith("VERIFIED FACTS:"):
            section = "verified"
        elif line.startswith("UNCERTAIN CLAIMS:"):
            section = "uncertain"
        elif line.startswith("CONTRADICTIONS:"):
            section = "contradictions"
        elif line.startswith("CONSENSUS:"):
            section = "consensus"
        elif line.startswith("- ") and section in ("verified", "uncertain", "contradictions"):
            result[{
                "verified": "verified_facts",
                "uncertain": "uncertain_claims",
                "contradictions": "contradictions"
            }[section]].append(line[2:])
        elif section == "consensus" and line:
            result["consensus"] += line + " "

    result["consensus"] = result["consensus"].strip()
    return result
