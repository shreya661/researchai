from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from db.database import init_db
from api.research import router as research_router
from api.history import router as history_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="ResearchLab AI",
    description="Multi-agent research and report generation API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ] + [origin for origin in [os.environ.get("FRONTEND_URL", "")] if origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(research_router)
app.include_router(history_router)


@app.get("/")
async def root():
    return {"message": "ResearchLab AI is running 🚀", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "ok"}
