"""
Coordinator Agent — orchestrates the full multi-agent research pipeline using LangGraph.
"""
from typing import TypedDict, Optional
# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, END

from agents.search_agent import run_search_agent
from agents.research_agent import run_research_agent
from agents.factcheck_agent import run_factcheck_agent
from agents.report_agent import run_report_agent


# ── State Schema ────────────────────────────────────────────────────────────
class ResearchState(TypedDict):
    topic: str
    domain: str
    search_results: Optional[list]
    summaries: Optional[list]
    verified_facts: Optional[dict]
    report_markdown: Optional[str]
    citations: Optional[list]
    error: Optional[str]
    current_agent: str


# ── Node Functions ──────────────────────────────────────────────────────────
def search_node(state: ResearchState) -> ResearchState:
    try:
        results = run_search_agent(state["topic"], state.get("domain", "general"))
        return {**state, "search_results": results, "current_agent": "research"}
    except Exception as e:
        return {**state, "error": f"Search failed: {str(e)}"}


def research_node(state: ResearchState) -> ResearchState:
    try:
        summaries = run_research_agent(state["topic"], state["search_results"], state.get("domain", "general"))
        return {**state, "summaries": summaries, "current_agent": "factcheck"}
    except Exception as e:
        return {**state, "error": f"Research failed: {str(e)}"}


def factcheck_node(state: ResearchState) -> ResearchState:
    try:
        verified = run_factcheck_agent(state["topic"], state["summaries"], state.get("domain", "general"))
        return {**state, "verified_facts": verified, "current_agent": "report"}
    except Exception as e:
        return {**state, "error": f"Fact-check failed: {str(e)}"}


def report_node(state: ResearchState) -> ResearchState:
    try:
        result = run_report_agent(state["topic"], state["verified_facts"], state["summaries"], state.get("domain", "general"))
        return {
            **state,
            "report_markdown": result["markdown"],
            "citations": result["citations"],
            "current_agent": "done",
        }
    except Exception as e:
        return {**state, "error": f"Report generation failed: {str(e)}"}


def should_continue(state: ResearchState) -> str:
    """Route to next node or END if error occurred."""
    if state.get("error"):
        return END
    return state.get("current_agent", END)


# ── Build the Graph ─────────────────────────────────────────────────────────
def build_pipeline():
    graph = StateGraph(ResearchState)

    graph.add_node("search", search_node)
    graph.add_node("research", research_node)
    graph.add_node("factcheck", factcheck_node)
    graph.add_node("report", report_node)

    graph.set_entry_point("search")

    graph.add_conditional_edges("search", should_continue, {
        "research": "research",
        END: END,
    })
    graph.add_conditional_edges("research", should_continue, {
        "factcheck": "factcheck",
        END: END,
    })
    graph.add_conditional_edges("factcheck", should_continue, {
        "report": "report",
        END: END,
    })
    graph.add_edge("report", END)

    return graph.compile()


# ── Main Entry Point ─────────────────────────────────────────────────────────
async def run_pipeline(
    topic: str,
    domain: str = "general",
    on_agent_update=None
) -> ResearchState:
    """
    Run the full research pipeline.
    on_agent_update(agent_name, message) is called at each agent transition.
    """
    pipeline = build_pipeline()

    initial_state: ResearchState = {
        "topic": topic,
        "domain": domain,
        "search_results": None,
        "summaries": None,
        "verified_facts": None,
        "report_markdown": None,
        "citations": None,
        "error": None,
        "current_agent": "search",
    }

    if on_agent_update:
        await on_agent_update("coordinator", f"Starting research on: {topic}")

    agent_messages = {
        "search": "🔍 Searching the web for sources...",
        "research": "📖 Reading and summarizing sources...",
        "factcheck": "✅ Verifying facts across sources...",
        "report": "📝 Generating final report...",
        "done": "🎉 Report complete!",
    }

    final_state = initial_state
    async for state in pipeline.astream(initial_state):
        # LangGraph streams node outputs; get the last state
        for node_name, node_state in state.items():
            final_state = node_state
            agent = node_state.get("current_agent", "")
            if on_agent_update and agent in agent_messages:
                await on_agent_update(agent, agent_messages[agent])

    return final_state
