---
name: rulees-backend-module
description: >
  Padrão oficial para criar ou estender um módulo do backend do Rulees (FastAPI).
  Use ao adicionar endpoints, models, schemas, services, regras de status (lifecycle),
  permissões ou eventos no backend — ex.: novo domínio (requirements, exports,
  integrations, billing), novo endpoint num módulo existente, nova migration/model.
  Garante multi-tenancy, RBAC, auditoria, usage events e estrutura modular corretos.
---

# Rulees — Padrão de Módulo Backend

Módulo canônico de referência: `backend/app/modules/projects/`. **Sempre espelhe um
módulo existente** antes de criar estrutura nova.

## Estrutura de um módulo

```
app/modules/<dominio>/
  __init__.py
  router.py        # HTTP: valida input, checa permissão, chama service, retorna response
  service.py       # regra de negócio, transações, audit/usage, eventos (quando há lógica)
  repository.py    # acesso a banco com filtro tenant_id/project_id (quando vale separar)
  models.py        # ORM SQLAlchemy 2.0 (Mapped/mapped_column)
  schemas.py       # Pydantic request/response
  lifecycle.py     # transições de status / regras de workflow (se tiver máquina de estado)
  events.py        # payloads de eventos internos / mapeamento WebSocket (se aplicável)
  tests/
```

Módulos simples (CRUD) podem ter lógica direto no `router.py` (como `projects`). Use
`service.py`/`lifecycle.py` quando houver regra de negócio ou máquina de estado.

## Convenções de `models.py`

```python
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Thing(Base):
    __tablename__ = "things"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), index=True)        # SEMPRE
    project_id: Mapped[str] = mapped_column(String(36), index=True)       # se pertence a projeto
    status: Mapped[str] = mapped_column(String(40), default="...", index=True)
    created_by: Mapped[str] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

Regras: IDs são UUID `str(36)`. Timestamps `DateTime(timezone=True)`. **Soft delete** via
`archived_at`/`deleted_at` para entidades auditáveis (projects, meetings, business_rules,
documents). **Nunca** soft delete em `audit_logs`, `usage_events`, `consent_records`,
`rule_versions` (são imutáveis). Status vai em **coluna própria**, nunca dentro de JSONB.

## Convenções de `router.py`

```python
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.errors import not_found
from app.db.session import get_db
from app.dependencies import RequestContext, get_request_context
from app.modules.audit.service import write_audit_log
from app.modules.usage.service import write_usage_event
from app.modules.permissions.service import require_permission

router = APIRouter()

@router.post("", response_model=ThingResponse)
def create_thing(payload: ThingCreate,
                 context: RequestContext = Depends(get_request_context),
                 db: Session = Depends(get_db)) -> Thing:
    require_permission(context, "thing.create")           # 1. RBAC primeiro
    thing = Thing(tenant_id=context.tenant_id, created_by=context.user_id, ...)
    db.add(thing); db.flush()                              # 2. flush p/ obter id
    write_audit_log(db, tenant_id=context.tenant_id, user_id=context.user_id,
                    action="thing.create", resource_type="thing", resource_id=thing.id)
    write_usage_event(db, tenant_id=context.tenant_id, user_id=context.user_id,
                      event_type="thing_created")
    db.commit(); db.refresh(thing)                         # 3. commit + refresh
    return thing

@router.get("/{thing_id}", response_model=ThingResponse)
def get_thing(thing_id: str,
              context: RequestContext = Depends(get_request_context),
              db: Session = Depends(get_db)) -> Thing:
    require_permission(context, "thing.view")
    thing = db.get(Thing, thing_id)
    if thing is None or thing.tenant_id != context.tenant_id:   # isolamento de tenant
        raise not_found("Thing not found")                       # not_found, não forbidden
    return thing
```

Pontos fixos:
- Contexto via `get_request_context` → `RequestContext(user, tenant, role)` com
  `context.tenant_id` / `context.user_id`. Tenant vem do header `X-Tenant-Id`.
- **Listagem** sempre `.where(Model.tenant_id == context.tenant_id)`.
- Erros via helpers de `app/core/errors.py`: `not_found, forbidden, bad_request,
  conflict, unauthorized` (nunca levantar `HTTPException` cru).
- Padrão de transação: `db.add` → `db.flush` → audit/usage → `db.commit` → `db.refresh`.

## `schemas.py` (Pydantic)

Response models leem do ORM com `model_config = ConfigDict(from_attributes=True)`.
Separe `XCreate` (entrada) de `XResponse` (saída). Valide tamanho/normalização aqui.

## Checklist ao adicionar um módulo/endpoint

1. [ ] `models.py` com `tenant_id` indexado, UUID, timestamps, soft delete se auditável.
2. [ ] `schemas.py` com Create/Response.
3. [ ] Endpoint com `require_permission(context, "<acao>")` em **toda mutação**.
4. [ ] Filtro `tenant_id` em toda leitura; cross-tenant → `not_found`.
5. [ ] `write_audit_log` em ações críticas; `write_usage_event` quando relevante.
6. [ ] Registrar a ação nova em `ROLE_ACTIONS` (`app/modules/permissions/service.py`)
       para os papéis certos (admin tem `*`).
7. [ ] Se tem status: adicionar enum em `app/shared/enums.py` e `lifecycle.py` com transições.
8. [ ] Incluir o router em `app/main.py` (`app.include_router(...)`).
9. [ ] Teste em `tests/` (espelhar `tests/test_mvp_flow.py`). Rodar `pytest -q`.

## Matriz de papéis (resumo — fonte: `documentos/Matriz de Permissões.docx`)

| Papel | Pode |
|---|---|
| **admin** | tudo (`*`) |
| **manager** | tudo operacional + `audit.view`, `usage.view` |
| **member** | criar/operar reunião, aprovar/rejeitar regra, gerar/exportar documento |
| **viewer** | somente `*.view` (read-only — nunca mutação nem `audio.chunk.create`) |

Para detalhes de permissão por módulo, ver `documentos/Matriz de Permissões.docx`.
