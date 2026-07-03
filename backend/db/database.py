from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./researchlab.db"
)

if DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
else:
    engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        from db.models import ResearchSession  # noqa
        await conn.run_sync(Base.metadata.create_all)
        # Safe migration if table already exists
        try:
            if DATABASE_URL.startswith("sqlite"):
                await conn.execute(text("ALTER TABLE research_sessions ADD COLUMN domain VARCHAR(100) DEFAULT 'general';"))
            else:
                await conn.execute(text("ALTER TABLE research_sessions ADD COLUMN IF NOT EXISTS domain VARCHAR(100) DEFAULT 'general';"))
        except Exception:
            pass

