---
name: rulees
description: >
  Skill central de desenvolvimento do Rulees — plataforma SaaS B2B (AI Requirements
  Intelligence Platform) que transforma reuniões em regras de negócio rastreáveis.
  Use SEMPRE que a tarefa envolver o projeto Rulees: criar/alterar módulos do backend
  (FastAPI), telas do frontend (React/Vite), banco (PostgreSQL/pgvector), reuniões em
  tempo real (WebSocket), pipeline de IA, Rules Ledger, permissões/multi-tenancy,
  documentos/exportação, billing/uso, ou qualquer dúvida sobre arquitetura, stack e
  convenções. Carrega o contexto do projeto e aponta para as skills específicas.
---

# Rulees — Skill de Desenvolvimento

## O que é o Rulees

Plataforma SaaS B2B que transforma reuniões de negócio em **regras claras, decisões,
dúvidas, histórias de usuário, critérios de aceite e documentação rastreável**.
O diferencial **não** é resumir reunião — é o **Rules Ledger** (governança de regras
com aprovação humana) e a **rastreabilidade anti-alucinação** (toda regra aponta para
a fala de origem).

- **Domínio:** rulees.com.br
- **Categoria:** AI Requirements Intelligence Platform
- **Documentação-fonte (visão v1.0):** pasta `documentos/` (30 `.docx`)
- **Mapa de conclusão:** `docs/PROJECT_COMPLETION_BACKLOG.md`

## Fluxo principal do produto

```
Conta → Tenant → Projeto → Reunião → Consentimento → Tempo real (áudio/STT)
      → Transcrição → Agentes de IA → Regras candidatas → Aprovação humana
      → Documento → PDF / Jira / Confluence
```

## Stack (confirmada no código)

| Camada | Tecnologia |
|---|---|
| Backend | Python + FastAPI + Pydantic + SQLAlchemy 2.0 (`Mapped`/`mapped_column`) |
| Banco | PostgreSQL + pgvector (prod) · SQLite como fallback local sem Docker |
| Migrations | Alembic (a implementar — hoje usa `Base.metadata.create_all`) |
| Cache/fila | Redis (Docker) · worker async (Arq) a implementar |
| Frontend | React 19 + TypeScript + Vite + TanStack Query + Zustand + Zod + lucide-react |
| IA | LangGraph + provider LLM (heurística local hoje) — ver skill `rulees-ai-agents` |
| Realtime | WebSocket nativo — ver skill `rulees-realtime-events` |

## Layout do repositório

```
backend/      FastAPI modular monolith (app/core, app/db, app/modules/<dominio>, app/shared)
frontend/     React + Vite (src/App.tsx por enquanto; evoluir p/ features/ por domínio)
infra/        docker-compose.yml (postgres pgvector + redis)
scripts/      dev.ps1
docs/         backlog vivo (PROJECT_COMPLETION_BACKLOG.md)
documentos/   30 .docx — visão de produto/arquitetura (read-only, é o "norte")
```

Backend já tem módulos: `auth, projects, meetings, realtime, rules_ledger, questions,
decisions, documents, audit, usage, permissions`.

## Invariantes inegociáveis (valem para TODO código)

1. **Multi-tenancy:** toda query operacional filtra por `tenant_id`; nunca retornar dado
   de outro tenant (responder `not_found`, não `forbidden`, para não vazar existência).
2. **Consentimento antes da reunião:** reunião não vai para `active` sem `ConsentRecord`.
3. **Aprovação humana:** a IA **nunca** marca regra como `approved`. Só Admin/Manager/Member
   com permissão `rule.approve`.
4. **Rastreabilidade:** toda saída de IA carrega `source_references` (fala de origem).
5. **Auditoria:** ação crítica (criar/aprovar/exportar/finalizar) gera `write_audit_log`.
6. **RBAC:** toda mutação chama `require_permission(context, "acao")`. Ver `rulees-backend-module`.
7. **Backend é a fonte da verdade:** validação no servidor, nunca confiar no frontend/WS.

## Rodar e testar

```powershell
# Backend
cd backend; .\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
.\.venv\Scripts\python.exe -m pytest -q          # testes (forçam SQLite via conftest)

# Frontend
cd frontend; npm install; npm run dev -- --host 127.0.0.1 --port 5173

# Infra local (Postgres pgvector + Redis)
docker compose -f infra/docker-compose.yml up -d
```

## Skills específicas (carregue conforme a tarefa)

- **`rulees-backend-module`** — criar/estender módulo do backend no padrão exato.
- **`rulees-ai-agents`** — contrato de saída dos agentes de IA + regras anti-alucinação.
- **`rulees-rules-ledger`** — máquina de estados das regras e transições permitidas.
- **`rulees-realtime-events`** — contratos e segurança dos eventos WebSocket.

## Subagentes úteis

- **`rulees-reviewer`** — revisa um diff contra os 7 invariantes acima.
- **`rulees-spec-auditor`** — confere uma feature contra os critérios de aceite (`AC-*`).
- **`rulees-ai-engineer`** — implementa/mantém o pipeline LangGraph multiagente.

## Regras de ouro ao implementar

- Espelhe um módulo existente (`projects` é o exemplo canônico) antes de inventar padrão.
- Não cresça o escopo: siga o backlog `P0 → P1` em `docs/PROJECT_COMPLETION_BACKLOG.md`.
- Texto/identidade visual em pt-BR; identificadores e código em inglês.
- Sem segredos no código e sem PII/áudio bruto em logs.
