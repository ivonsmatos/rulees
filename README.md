# Rulees

Rulees is an AI Requirements Intelligence Platform. It turns business meetings into traceable business rules, questions, decisions, documents, and exportable artifacts.

This repository was initialized from the documentation in `documentos/`.

Current completion map: `docs/PROJECT_COMPLETION_BACKLOG.md`.

## MVP direction

The first executable slice follows the documented flow:

Conta -> Tenant -> Projeto -> Reuniao -> Consentimento -> Tempo real -> Regras -> Documento

## Repository layout

```text
backend/      FastAPI modular monolith
backend/alembic/ Database migrations
frontend/     React + Vite PWA-ready app
infra/        Local infrastructure helpers
scripts/      Developer scripts
.claude/      Rulees development skills and review agents
documentos/   Original product and architecture documentation
```

## Local start

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Frontend:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

With Docker running, start Postgres and Redis:

```powershell
docker compose -f infra/docker-compose.yml up -d
```

Then run the backend with:

```powershell
$env:DATABASE_URL='postgresql+psycopg://rulees:rulees@127.0.0.1:55432/rulees'
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

The backend still defaults to a local SQLite database at `backend/rulees.db` so the project can boot even without Docker.

## Docker images

Backend image:

```powershell
docker build -t rulees-backend:local -f backend/Dockerfile backend
docker run --rm -p 8001:8001 `
  -e DATABASE_URL='postgresql+psycopg://rulees:rulees@host.docker.internal:55432/rulees' `
  -e REDIS_URL='redis://host.docker.internal:6379/0' `
  -e SECRET_KEY='local-dev-secret' `
  rulees-backend:local
```

Frontend image:

```powershell
cd frontend
npm install
npm run build
cd ..
docker build -t rulees-frontend:local -f frontend/Dockerfile frontend
docker run --rm -p 5173:5173 rulees-frontend:local
```

## Database migrations

Alembic is configured as the migration path for the backend schema.

Fresh database:

```powershell
cd backend
$env:DATABASE_URL='postgresql+psycopg://rulees:rulees@127.0.0.1:55432/rulees'
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Existing local development database that was already created by the app bootstrap:

```powershell
cd backend
$env:DATABASE_URL='postgresql+psycopg://rulees:rulees@127.0.0.1:55432/rulees'
.\.venv\Scripts\python.exe -m alembic stamp head
```

Only use `stamp head` after confirming the current tables already match the initial migration. App startup still keeps `create_all` as a local bootstrap fallback, but new schema changes should be added through Alembic revisions.

## Local API

- `GET /health`
- `GET /health/dependencies`
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/auth/tenants`
- `GET /api/auth/tenant/members`
- `PATCH /api/auth/tenant/members/{member_id}`
- `GET /api/auth/tenant/invites`
- `POST /api/auth/tenant/invites`
- `GET /api/auth/invites/pending`
- `POST /api/auth/tenant/invites/{invite_id}/accept`
- `GET /api/projects`
- `POST /api/projects`
- `GET /api/projects/templates`
- `POST /api/projects/templates`
- `POST /api/projects/templates/{template_id}/projects`
- `GET /api/projects/{project_id}`
- `PATCH /api/projects/{project_id}`
- `POST /api/projects/{project_id}/archive`
- `GET /api/projects/{project_id}/glossary`
- `POST /api/projects/{project_id}/glossary`
- `PATCH /api/projects/{project_id}/glossary/{term_id}`
- `GET /api/projects/{project_id}/members`
- `POST /api/projects/{project_id}/members`
- `POST /api/projects/{project_id}/meetings`
- `POST /api/meetings/{meeting_id}/consent`
- `POST /api/meetings/{meeting_id}/consent/revoke`
- `GET /api/meetings/{meeting_id}/participants`
- `POST /api/meetings/{meeting_id}/participants`
- `GET /api/meetings/{meeting_id}/lifecycle-events`
- `POST /api/meetings/{meeting_id}/start`
- `POST /api/meetings/{meeting_id}/pause`
- `POST /api/meetings/{meeting_id}/resume`
- `POST /api/meetings/{meeting_id}/finish`
- `GET /api/meetings/{meeting_id}/state`
- `GET /api/projects/{project_id}/rules`
- `POST /api/rules/{rule_id}/approve`
- `POST /api/rules/{rule_id}/reject`
- `GET /api/rules/{rule_id}/versions`
- `POST /api/rules/{rule_id}/versions`
- `GET /api/meetings/{meeting_id}/questions`
- `GET /api/meetings/{meeting_id}/decisions`
- `GET /api/meetings/{meeting_id}/agent-runs`
- `GET /api/projects/{project_id}/rag/search?query=...`
- `GET /api/projects/{project_id}/rag/embeddings`
- `GET /api/documents`
- `POST /api/meetings/{meeting_id}/documents/generate`
- `GET /api/documents/{document_id}/sections`
- `GET /api/documents/{document_id}/versions`
- `POST /api/documents/{document_id}/versions`
- `GET /api/documents/{document_id}/export/pdf`
- `GET /api/audit/logs`
- `GET /api/usage/events`
- `GET /api/usage/summary`
- `GET /api/billing/status`
- `WS /ws/meetings/{meeting_id}?token=...`

Local backend URL used by the frontend: `http://127.0.0.1:8001`.

Backend tests force `sqlite:///./rulees_test.sqlite` through `backend/tests/conftest.py`, so the suite can run even when Docker is closed.

RBAC is centralized in `backend/app/modules/permissions/service.py`.

Realtime audio supports two `audio.chunk` payloads:

- demo text: `{ "text": "Quando..." }`
- captured browser audio: `{ "audio_base64": "...", "mime_type": "audio/webm", "sequence": 1 }`

Captured audio is validated and tracked, but still uses a deterministic transcript placeholder until a real STT provider is connected.

Optional STT provider configuration:

```powershell
$env:STT_PROVIDER='deepgram'
$env:DEEPGRAM_API_KEY='...'
$env:DEEPGRAM_MODEL='nova-3'
$env:DEEPGRAM_LANGUAGE='pt-BR'
$env:STT_DIARIZE='true'
```

Without these values the backend uses `STT_PROVIDER=mock`, which keeps tests and local development deterministic. Transcript chunks store partial/final state, start/end timestamps, speaker labels, language, confidence and provider metadata when the provider returns them.

RAG/memory uses `semantic_embeddings` with strict tenant/project filtering. The current local embedder is deterministic (`rulees-hash-v1`) so tests do not depend on an external embeddings provider. The `20260630_0003` migration enables `pgvector` on PostgreSQL, preparing the database for real vector search.

`/health/dependencies` checks database, Redis and local storage. The backend uses FastAPI lifespan startup and keeps `AUTO_CREATE_TABLES=true` as a local bootstrap fallback; production should run Alembic before booting the app.

## Notes

This is Sprint 0/1 foundation code. It intentionally keeps AI/STT providers as deterministic local demo behavior, while preserving the documented boundaries: tenant context, consent before meeting start, auditable critical actions, human approval for rules, and backend as source of truth.
