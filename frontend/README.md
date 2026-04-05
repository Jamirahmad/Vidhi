# Vidhi - Legal Case Research and Document Automation

Vidhi is an assistive legal research and document automation platform for the Indian legal ecosystem. The backend now uses a LangChain-powered RAG pipeline with a local Chroma vector store.

## Core Principles
- Human verification is mandatory.
- No fabricated case laws or citations.
- Vidhi supports research and drafting, not legal advice.

## Architecture in This Repo
- Frontend: Vite + React (`src/`)
- Backend API server: FastAPI (`backend/app/main.py`)
- RAG stack: LangChain + Chroma (`backend/app/knowledge`)
- Public-source ingestion: Supreme Court of India website (`https://www.sci.gov.in/`)

## Required Backend Endpoints
- `GET /api/v1/knowledge-base/search?q=...`
- `POST /api/v1/knowledge-base/refresh?years=5&limit=200`
- `GET /api/v1/health`
- Existing agent endpoints under `/api/v1/agents/*`

## Environment Setup
Create a single repo-root `.env` from `.env.example`:
- `OPENROUTER_API_KEY`
- `VIDHI_LLM_MODEL` (example: `openai/gpt-4.1-mini`)
- `OPENROUTER_SITE_URL` (example: `http://localhost:5173`)
- `OPENROUTER_APP_NAME` (example: `Vidhi`)
- `OPENROUTER_MAX_TOKENS` (example: `1800`)
- `VIDHI_KB_SCOPE` (`indian_penal_courts` recommended)
- `VIDHI_VERDICT_ONLY` (`true` to return only cases with verdict markers)
- `VIDHI_RAG_MODE` (`regressive` recommended)
- `VIDHI_LOCAL_MIN_RESULTS` (default `3`)
- `VIDHI_LOCAL_MIN_TOP_SCORE` (default `0.08`)
- `VIDHI_AUTO_REFRESH_PUBLIC_CASES` (`true` recommended to auto-fetch public cases when index is empty)
- `VIDHI_WEB_SEARCH_PROVIDER` (`serpapi` or 
one`)
- `SERPAPI_API_KEY` (required when provider is `serpapi`)
- `VIDHI_WEB_SEARCH_COUNTRY` (`IN` recommended)
- `VIDHI_WEB_SEARCH_LANGUAGE` (`en` recommended)
- `VIDHI_EXTERNAL_KNOWLEDGE_ENDPOINTS` (optional)
- `VIDHI_EXTERNAL_KNOWLEDGE_TIMEOUT_S` (default `8`)
- `PORT` (default `8000`)

Frontend keys in the same root `.env`:
- `VITE_VIDHI_API_BASE_URL=http://localhost:8000/api/v1`

## Run Locally
Terminal 1 (backend):
```bash
pip install -r backend/requirements.txt
npm run backend:dev
```

Terminal 2 (frontend):
```bash
npm run dev
```

## Load Last 5 Years Public Cases into RAG
Call refresh endpoint:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/knowledge-base/refresh?years=5&limit=200"
```

This fetches publicly accessible entries from the Supreme Court of India website, filters to recent criminal/penal context, stores JSON under `backend/data/knowledge/court_cases`, and ingests into Chroma.

## Quality Gates
```bash
npm run test
npm run build
```

## Ethics and Limitations
- Vidhi does not provide legal advice.
- Outputs must be reviewed by qualified legal professionals before use.


