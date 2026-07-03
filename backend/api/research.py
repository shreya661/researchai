"""
Research API routes — start research, stream progress, get report, download PDF.
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.database import get_db
from db.models import ResearchSession
from models.schemas import ResearchRequest, SessionStartResponse, SessionStatusResponse, Citation
from agents.coordinator import run_pipeline
from tools.pdf_generator import markdown_to_pdf

router = APIRouter(prefix="/api/research", tags=["research"])

# Track active WebSocket connections: session_id -> list of websockets
_active_connections: dict[str, list[WebSocket]] = {}


# ── Start Research ──────────────────────────────────────────────────────────
@router.post("/start", response_model=SessionStartResponse)
async def start_research(request: ResearchRequest, db: AsyncSession = Depends(get_db)):
    session_id = str(uuid.uuid4())
    session = ResearchSession(
        id=session_id,
        topic=request.topic,
        domain=request.domain,
        status="running",
        current_agent="search",
    )
    db.add(session)
    await db.commit()

    # Run pipeline in background
    asyncio.create_task(_run_research_task(session_id, request.topic, request.domain))

    return SessionStartResponse(
        session_id=session_id,
        topic=request.topic,
        status="running",
        domain=request.domain,
    )


# ── Background Research Task ────────────────────────────────────────────────
async def _run_research_task(session_id: str, topic: str, domain: str = "general"):
    from db.database import AsyncSessionLocal

    async def on_agent_update(agent: str, message: str):
        """Broadcast agent progress to all connected WebSocket clients."""
        event = {
            "session_id": session_id,
            "agent": agent,
            "status": "running",
            "message": message,
        }
        await _broadcast(session_id, event)

        # Update DB current_agent
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ResearchSession).where(ResearchSession.id == session_id))
            session = result.scalar_one_or_none()
            if session:
                session.current_agent = agent
                await db.commit()

    try:
        final_state = await run_pipeline(topic, domain, on_agent_update=on_agent_update)

        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ResearchSession).where(ResearchSession.id == session_id))
            session = result.scalar_one_or_none()
            if session:
                if final_state.get("error"):
                    session.status = "error"
                    session.error_message = final_state["error"]
                else:
                    session.status = "done"
                    session.report_markdown = final_state.get("report_markdown")
                    session.citations = final_state.get("citations")
                    session.search_results = final_state.get("search_results")
                    session.summaries = [
                        {k: v for k, v in s.items() if k != "llm_analysis"}
                        for s in (final_state.get("summaries") or [])
                    ]
                    session.verified_facts = final_state.get("verified_facts")
                    session.current_agent = "done"
                    session.completed_at = datetime.now(timezone.utc)
                await db.commit()

        # Notify completion
        await _broadcast(session_id, {
            "session_id": session_id,
            "agent": "done",
            "status": "done" if not final_state.get("error") else "error",
            "message": "Report complete!" if not final_state.get("error") else final_state["error"],
        })
        if session_id in _active_connections:
            del _active_connections[session_id]

    except Exception as e:
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(ResearchSession).where(ResearchSession.id == session_id))
            session = result.scalar_one_or_none()
            if session:
                session.status = "error"
                session.error_message = str(e)
                await db.commit()
        await _broadcast(session_id, {
            "session_id": session_id,
            "agent": "error",
            "status": "error",
            "message": str(e),
        })
        if session_id in _active_connections:
            del _active_connections[session_id]


# ── WebSocket Progress Stream ───────────────────────────────────────────────
@router.websocket("/ws/{session_id}")
async def websocket_progress(websocket: WebSocket, session_id: str):
    await websocket.accept()
    _active_connections.setdefault(session_id, []).append(websocket)
    try:
        while True:
            await asyncio.sleep(30)  # keep alive
    except WebSocketDisconnect:
        _active_connections.get(session_id, []).remove(websocket)


async def _broadcast(session_id: str, event: dict):
    connections = _active_connections.get(session_id, [])
    dead = []
    for ws in connections:
        try:
            await ws.send_text(json.dumps(event))
        except Exception:
            dead.append(ws)
    for ws in dead:
        connections.remove(ws)


# ── Get Session Status ──────────────────────────────────────────────────────
@router.get("/{session_id}/status", response_model=SessionStatusResponse)
async def get_status(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ResearchSession).where(ResearchSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    citations = [Citation(**c) for c in (session.citations or [])]

    return SessionStatusResponse(
        session_id=session.id,
        topic=session.topic,
        status=session.status,
        current_agent=session.current_agent,
        report_markdown=session.report_markdown,
        citations=citations,
        error_message=session.error_message,
        created_at=session.created_at,
        completed_at=session.completed_at,
        domain=session.domain or "general",
    )


# ── Download PDF ────────────────────────────────────────────────────────────
@router.get("/{session_id}/pdf")
async def download_pdf(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ResearchSession).where(ResearchSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session or session.status != "done":
        raise HTTPException(status_code=404, detail="Report not ready")

    pdf_bytes = markdown_to_pdf(
        topic=session.topic,
        markdown_text=session.report_markdown or "",
        citations=session.citations or [],
    )

    filename = f"researchlab_{session.topic[:30].replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
