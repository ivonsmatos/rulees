---
name: rulees-realtime-events
description: >
  Contratos e segurança dos eventos WebSocket do Rulees (reunião em tempo real).
  Use ao implementar/alterar a conexão WebSocket, envio de áudio/chunks, eventos de
  transcrição e de IA ao vivo, autenticação do socket, ou qualquer evento realtime
  entre frontend e backend. Garante o envelope padrão e as regras WS-SEC.
---

# Rulees — Eventos WebSocket (Tempo Real)

Fonte: `documentos/Contratos de Eventos WebSocket.docx`.
Implementação: `backend/app/modules/realtime/websocket.py`.
Cliente: `frontend/src/App.tsx` (`connectSocket`).

## Endpoint

```
wss://api.rulees.com.br/ws/meetings/{meeting_id}?token={access_token}
# local: ws://127.0.0.1:8001/ws/meetings/{meeting_id}?token=...
```

A autenticação é por **token na query string** (não há header em WS no browser). O backend
faz `decode_access_token(token)` e checa `TenantMember` para o tenant da reunião.

Códigos de fechamento: `4401` token inválido · `4403` sem acesso à reunião ·
`4404` reunião inexistente.

## Regras de segurança (WS-SEC — todas validadas no backend)

| Regra | Descrição |
|---|---|
| **WS-SEC-001** | Conexão exige autenticação (token válido). |
| **WS-SEC-002** | Usuário precisa ter acesso à reunião (membership do tenant). |
| **WS-SEC-003** | Viewer **não** pode enviar áudio (`audio.chunk` exige `audio.chunk.create`). |
| **WS-SEC-004** | Apenas reunião `active` aceita `audio.chunk`. |
| **WS-SEC-005** | Todo evento é validado no backend — nunca confiar no cliente. |

## Envelope padrão dos eventos

```json
{ "event_type": "namespace.action", "payload": { } }
```

## Eventos cliente → servidor

| event_type | payload | Regra |
|---|---|---|
| `system.ping` | `{}` | Responde `system.pong`. |
| `client.join_meeting` | `{}` | Responde `client.joined_meeting`. |
| `audio.chunk` | `{ "text": "..." }` (demo) / áudio | Exige `audio.chunk.create` + reunião `active`. |

## Eventos servidor → cliente

| event_type | payload | Quando |
|---|---|---|
| `client.connected` | `{ meeting_id }` | Logo após `accept()`. |
| `client.joined_meeting` | `{ meeting_id, status }` | Resposta ao join. |
| `system.pong` | `{}` | Resposta ao ping. |
| `transcript.final` | chunk normalizado (Scribe) | Novo trecho transcrito. |
| `ai.rule.detected` | regra candidata (Observer) | Regra detectada ao vivo. |
| `ai.question.suggested` | pergunta (Inquisitor) | Lacuna detectada. |
| `ai.decision.detected` | decisão (Decision) | Decisão detectada. |
| `error.validation` | `{ code, message }` | Evento recusado/ inválido. |

## Fluxo ao vivo

1. Frontend chama `POST /api/meetings/{id}/start` (exige consentimento) → abre o socket.
2. Envia `client.join_meeting`.
3. Envia `audio.chunk` → backend valida (WS-SEC-003/004) → Scribe normaliza →
   emite `transcript.final` → Observer roda → emite `ai.rule.detected` etc.
4. `pause`/`finish` fecham o socket pelo cliente e mudam o estado no backend.

## Checklist ao adicionar um evento

1. [ ] Definir `event_type` no padrão `namespace.action`.
2. [ ] Validar **no backend**: reunião existe, estado correto, permissão do papel.
3. [ ] `audio.*` e mutações: checar `can_role`/`require_permission`.
4. [ ] Registrar `write_usage_event` quando o evento consome recurso (áudio/IA).
5. [ ] Recusar evento inválido com `error.validation` (nunca derrubar a conexão à toa).
6. [ ] Refletir o contrato no tipo `WsEvent` do frontend (`App.tsx`).
