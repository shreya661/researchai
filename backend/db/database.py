from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

# ── Vercel / cloud providers sometimes give a URL starting with "postgres://"
#    but SQLAlchemy requires "postgresql+asyncpg://".  Handle both.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# ── asyncpg does not understand ?sslmode=require, so strip it and use ssl=True
_connect_args = {}
if "sslmode=require" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("?sslmode=require", "").replace("&sslmode=require", "")
    _connect_args["ssl"] = "require"

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Please set it to a PostgreSQL connection string, e.g. "
        "postgresql+asyncpg://user:password@host:5432/dbname"
    )

# ── Create engine (PostgreSQL only — no SQLite) ──
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,       # reconnect stale connections
    connect_args=_connect_args,
)

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
            await conn.execute(
                text("ALTER TABLE research_sessions ADD COLUMN IF NOT EXISTS domain VARCHAR(100) DEFAULT 'general';")
            )
        except Exception:
            pass
