# Rulees Runbooks Operacionais

## Health check

Verificar API:

```powershell
Invoke-RestMethod http://127.0.0.1:8001/health
Invoke-RestMethod http://127.0.0.1:8001/health/dependencies
```

Verificar frontend:

```powershell
Invoke-WebRequest http://127.0.0.1:5173
```

## Migrations

Aplicar migrations no banco configurado em `backend/.env`:

```powershell
cd C:\wamp64\www\rulees\backend
python -m alembic upgrade head
python -m alembic check
```

## Metricas

Endpoint:

```powershell
Invoke-WebRequest http://127.0.0.1:8001/metrics
```

Metricas publicadas:

- `rulees_http_requests_total`
- `rulees_http_request_duration_seconds_avg`

Status de observabilidade:

```powershell
Invoke-RestMethod http://127.0.0.1:8001/observability/status
```

O middleware emite `traceparent` compatível com OpenTelemetry. Se `SENTRY_DSN` estiver configurado, o monitoramento de erros opera em modo Sentry; sem DSN, permanece em modo local.

## Rate limit

Configuracoes em `backend/.env`:

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=240
RATE_LIMIT_WINDOW_SECONDS=60
```

Resposta esperada quando o limite e atingido: HTTP `429` com `Retry-After`.

## Auditoria

Listar auditoria filtrada:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/api/audit/logs?action=rule.replace" -Headers @{
  Authorization="Bearer <token>"
  "X-Tenant-Id"="<tenant-id>"
}
```

Os detalhes de auditoria mascaram chaves sensiveis como `password`, `token`, `access_token`, `authorization`, `secret` e `api_key`.

Executar retention por tenant:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/api/audit/retention/run?retention_days=365" -Method Post -Headers @{
  Authorization="Bearer <token>"
  "X-Tenant-Id"="<tenant-id>"
}
```

## Exportacoes

Downloads diretos:

- `GET /api/documents/{document_id}/export/pdf`
- `GET /api/documents/{document_id}/export/markdown`
- `GET /api/documents/{document_id}/export/excel`
- `GET /api/documents/{document_id}/export/{pdf|markdown|excel}/signed-url`

Jobs sincronizados:

- `POST /api/documents/{document_id}/export-jobs` com `{"format":"pdf"}`
- `POST /api/documents/{document_id}/export-jobs` com `{"format":"markdown"}`
- `POST /api/documents/{document_id}/export-jobs` com `{"format":"excel"}`
- `POST /api/documents/{document_id}/export-jobs` com `{"format":"jira"}`
- `POST /api/documents/{document_id}/export-jobs` com `{"format":"confluence"}`

## P2 operacional

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/api/search/global?query=<termo>" -Headers @{ Authorization="Bearer <token>"; "X-Tenant-Id"="<tenant-id>" }
Invoke-RestMethod "http://127.0.0.1:8001/api/analytics/summary" -Headers @{ Authorization="Bearer <token>"; "X-Tenant-Id"="<tenant-id>" }
Invoke-RestMethod "http://127.0.0.1:8001/api/notifications" -Headers @{ Authorization="Bearer <token>"; "X-Tenant-Id"="<tenant-id>" }
```

Comparar versoes:

- `GET /api/documents/{document_id}/versions/diff?from_version=1&to_version=2`
- `GET /api/rules/{rule_id}/versions/diff?from_version=1&to_version=2`

## Testes de regressao

```powershell
cd C:\wamp64\www\rulees\backend
python -m pytest tests -q

cd C:\wamp64\www\rulees\frontend
npm run build
```
