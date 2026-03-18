# Backend (API + agents)

All Python code lives here: FastAPI app, LangGraph workflow, scoring agents (`core/`), and the LiveKit interviewer (`agent/`).

## Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

Copy `.env` into `backend/` (API keys, DB, etc.). Optional: default job description file `NEW-JD` in this folder.

## Run API

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Layout

| Path | Purpose |
|------|---------|
| `app/` | FastAPI routes, services, DB models |
| `core/` | LLM service, stage1/2/3 agents, GitHub verifier |
| `workflows/` | LangGraph funnel |
| `config/` | Logging |
| `agent/` | LiveKit voice interviewer worker |
| `data/` | Sample spreadsheets / exports |
| `NEW-JD` | Fallback job description text |
