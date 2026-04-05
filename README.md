# Vidhi Monorepo

Vidhi is an assistive legal research and document automation platform for the Indian legal ecosystem.

## Monorepo Layout
- `frontend` - Vite + React frontend
- `backend` - FastAPI backend
- `packages/contracts` - shared request/response workflow contracts
- `scripts` - local wrapper scripts

## Compatibility Commands (repo root)
- `npm run dev` - run web app
- `npm run build` - build web app
- `npm run test` - run web tests
- `npm run backend:setup` - install backend python dependencies
- `npm run backend:dev` - run backend API (`backend.app.main:app`)
- `npm run backend:smoke` - run backend smoke test

## Environment
- Single env template: `.env.example` (copy to `.env` at repo root for both web and API).
- Runtime mutable data can be externalized with `VIDHI_RUNTIME_DATA_DIR`.

## Workflow API (Async)
- `POST /api/v1/workflows` - queue workflow, returns `jobId`
- `GET /api/v1/workflows/{jobId}` - get queued/running/completed/failed status
- `POST /api/v1/workflows/sync` - compatibility adapter

## Quality Gates
- Web build: `npm run build`
- API syntax check: `python -m py_compile backend/app/main.py`
- CI: `.github/workflows/ci.yml`

## Ethics and Limitations
- Human verification is mandatory.
- No fabricated case laws or citations.
- Outputs are legal-research assistance and not legal advice.


## Backend venv
- Backend commands use isolated .venv-api to avoid global package conflicts (for example with crewai).
- Recreate environment: delete `.venv-api` then run `npm run backend:setup`.

