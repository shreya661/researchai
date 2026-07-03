# Reserch.Ai

Reserch.Ai is a full-stack multi-agent research assistant. It takes a research topic, searches the web, summarizes sources with Groq, cross-checks claims, and generates a citation-backed Markdown report that can be exported as a PDF.

The app is built with FastAPI, LangGraph, Tavily, Groq, SQLite or PostgreSQL, and a Vite React dashboard.

## Features

- Multi-agent workflow for search, summarization, fact checking, and report writing.
- Live progress updates in the dashboard through WebSockets.
- Domain-aware research modes for general, healthcare, education, policy, and science topics.
- Persistent research history stored in a SQL database.
- Citation list and PDF export for completed reports.
- Local-first development setup with `.env.example` and safe defaults.

## Architecture

```mermaid
flowchart LR
    User[User] --> Dashboard[React Dashboard]
    Dashboard -->|POST /api/research/start| API[FastAPI Backend]
    Dashboard <-->|WebSocket progress| API
    Dashboard -->|GET status/history/pdf| API
    API --> DB[(SQLite or PostgreSQL)]
    API --> Graph[LangGraph Coordinator]
    Graph --> Search[Search Agent]
    Search --> Tavily[Tavily Search API]
    Graph --> Research[Research Agent]
    Research --> Groq[Groq LLM]
    Graph --> FactCheck[Fact-Check Agent]
    FactCheck --> Groq
    Graph --> Report[Report Agent]
    Report --> Groq
    API --> PDF[PDF Generator]
```

## Agent Workflow

```mermaid
flowchart TD
    Start([Start Research]) --> Search[Search Agent]
    Search --> SearchCheck{Error?}
    SearchCheck -->|Yes| Failed([Save Error])
    SearchCheck -->|No| Research[Research Agent]
    Research --> ResearchCheck{Error?}
    ResearchCheck -->|Yes| Failed
    ResearchCheck -->|No| FactCheck[Fact-Check Agent]
    FactCheck --> FactCheckResult{Error?}
    FactCheckResult -->|Yes| Failed
    FactCheckResult -->|No| Report[Report Agent]
    Report --> Done([Save Report])
```

## Request Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as React Dashboard
    participant API as FastAPI
    participant WS as WebSocket
    participant LG as LangGraph
    participant DB as Database

    U->>UI: Enter topic and domain
    UI->>API: POST /api/research/start
    API->>DB: Create running session
    API-->>UI: Return session_id
    UI->>WS: Connect /api/research/ws/{session_id}
    API->>LG: Run pipeline in background
    LG-->>WS: Agent progress events
    LG->>API: Final report or error
    API->>DB: Persist result
    UI->>API: GET /api/research/{session_id}/status
    API-->>UI: Report, citations, status
```

## Project Structure

```text
capstone/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── agents/
│   │   ├── coordinator.py
│   │   ├── search_agent.py
│   │   ├── research_agent.py
│   │   ├── factcheck_agent.py
│   │   └── report_agent.py
│   ├── api/
│   │   ├── research.py
│   │   └── history.py
│   ├── db/
│   │   ├── database.py
│   │   └── models.py
│   ├── models/
│   │   └── schemas.py
│   └── tools/
│       ├── web_search.py
│       └── pdf_generator.py
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx
│       ├── pages/
│       │   ├── Home.jsx
│       │   └── Research.jsx
│       └── components/
│           ├── AgentTracker.jsx
│           ├── CitationList.jsx
│           └── ReportViewer.jsx
└── README.md
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, Vite, Axios |
| Backend | FastAPI, Uvicorn |
| Agent orchestration | LangGraph |
| LLM provider | Groq |
| Web search | Tavily |
| Database | SQLite by default, PostgreSQL supported |
| PDF export | ReportLab |

## Prerequisites

- Python 3.11 or newer
- Node.js 18 or newer
- Groq API key
- Tavily API key
- GitHub CLI only if you want to publish from the terminal

## Backend Setup

```bash
cd backend
python -m venv .venv
```

Activate the virtual environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
cp .env.example .env
```

On Windows Command Prompt:

```cmd
copy .env.example .env
```

Fill in your keys:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
DATABASE_URL=sqlite+aiosqlite:///./researchlab.db
```

Start the backend:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Useful backend links:

- API root: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health
- Swagger docs: http://127.0.0.1:8000/docs

## Frontend Setup

Open a second terminal:

```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1
```

Open the dashboard:

```text
http://127.0.0.1:5173
```

By default, the frontend calls:

```text
http://localhost:8000
```

You can override that with a frontend `.env` file:

```env
VITE_API_BASE=http://127.0.0.1:8000
```

## API Guide

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Backend health check |
| POST | `/api/research/start` | Start a research session |
| GET | `/api/research/{session_id}/status` | Get progress or final report |
| WS | `/api/research/ws/{session_id}` | Stream live agent updates |
| GET | `/api/research/{session_id}/pdf` | Download PDF report |
| GET | `/api/history` | List previous sessions |
| DELETE | `/api/history/{session_id}` | Delete a saved session |

Example start request:

```json
{
  "topic": "Quantum computing applications",
  "domain": "science"
}
```

Example response:

```json
{
  "session_id": "99fbc502-b2d9-4f96-8eb5-1ad899fb58d2",
  "topic": "Quantum computing applications",
  "status": "running",
  "domain": "science"
}
```

Example WebSocket event:

```json
{
  "session_id": "99fbc502-b2d9-4f96-8eb5-1ad899fb58d2",
  "agent": "research",
  "status": "running",
  "message": "Reading and summarizing sources...",
  "data": null
}
```

## Domain Modes

The pipeline accepts a `domain` value to tune prompts:

- `general`
- `healthcare`
- `education`
- `policy`
- `science`

Each mode changes what the research, verification, and report-writing agents prioritize.

## Validation

Frontend build:

```bash
cd frontend
npm run build
```

Backend smoke check after starting Uvicorn:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Environment And Security Notes

- Do not commit `backend/.env`.
- Do not commit `backend/researchlab.db`; it contains local session history.
- Rotate API keys if they were ever shared in chat, screenshots, or public commits.
- Use `.env.example` to document required variables without exposing real secrets.

## Production Notes

- Build the frontend with `npm run build`.
- Serve `frontend/dist` with a static host such as Nginx, Netlify, or Vercel.
- Run the backend with a production ASGI server configuration.
- Replace local SQLite with PostgreSQL for multi-user or deployed environments.
- Set explicit CORS origins for your production frontend domain.

## Author

Built by Shreya Patha as a capstone project.
