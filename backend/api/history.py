"""
History API routes — list and delete past research sessions.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from db.database import get_db
from db.models import ResearchSession
from models.schemas import HistoryItem

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=list[HistoryItem])
async def get_history(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ResearchSession).order_by(ResearchSession.created_at.desc()).limit(50)
    )
    sessions = result.scalars().all()
    return [
        HistoryItem(
            session_id=s.id,
            topic=s.topic,
            status=s.status,
            created_at=s.created_at,
            completed_at=s.completed_at,
            domain=s.domain or "general",
        )
        for s in sessions
    ]


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ResearchSession).where(ResearchSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.execute(delete(ResearchSession).where(ResearchSession.id == session_id))
    await db.commit()
    return {"message": "Session deleted"}
