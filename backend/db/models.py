from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from db.database import Base
import uuid


class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    topic = Column(String(500), nullable=False)
    domain = Column(String(100), default="general")
    status = Column(String(50), default="pending")   # pending | running | done | error
    current_agent = Column(String(100), nullable=True)
    search_results = Column(JSONB, nullable=True)
    summaries = Column(JSONB, nullable=True)
    verified_facts = Column(JSONB, nullable=True)
    report_markdown = Column(Text, nullable=True)
    citations = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
