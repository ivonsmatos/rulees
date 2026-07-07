---
name: rulees-rules-ledger
description: >
  Máquina de estados do Rules Ledger do Rulees e suas transições. Use ao implementar
  ou revisar criação de regra a partir da IA, aprovação/rejeição humana, detecção de
  conflito, versionamento (replaced/revoked), arquivamento, ou qualquer mudança de
  status de business_rule. Garante o controle humano e a rastreabilidade exigidos.
---

# Rulees — Rules Ledger (Governança de Regras)

Fonte: `documentos/Fluxo Completo do Rules Ledger.docx`.
Enum real: `RuleStatus` em `backend/app/shared/enums.py`.
Módulo: `backend/app/modules/rules_ledger/`.

## Conceito

O Rules Ledger é o **livro-razão das regras de negócio**: cada regra tem estado,
histórico, versão, fonte (fala da reunião) e responsável pela decisão. É o diferencial
do produto — não confundir com "lista de itens de ata".

- **Regra candidata:** criada pela IA (Observer). Sai sempre como `draft`. Não vale como
  oficial até passar por humano.
- **Regra oficial:** chegou a `approved` por ação humana (`rule.approve`).

## Estados (`RuleStatus`)

| Estado | Significado |
|---|---|
| `draft` | Recém-criada (pela IA ou manualmente). Ponto de partida. |
| `needs_review` | Precisa de revisão humana. |
| `in_validation` | Em validação (checagens / RAG em andamento). |
| `conflict_detected` | RAG Guardian achou conflito/duplicidade — exige resolução humana. |
| `approved` | Oficial. **Só por humano** com `rule.approve`. |
| `approved_incomplete_for_dev` | Aprovada para seguir, mas com lacunas conhecidas. |
| `rejected` | Recusada (`rule.reject`). |
| `replaced` | Substituída por uma versão mais nova (versionamento). |
| `revoked` | Revogada após ter sido aprovada. |
| `archived` | Arquivada (fim de vida, sem valor ativo). |

## Transições permitidas (workflow)

```
draft ─────────────► needs_review ─────► in_validation ─┬─► approved
  │                       │                              ├─► approved_incomplete_for_dev
  │                       │                              └─► conflict_detected ─► (humano)
  ├─► rejected                                                                     │
  └─► conflict_detected                                          conflict_detected ┘
                                                                  ├─► approved (resolvido)
approved ─► replaced | revoked | archived                        └─► rejected
rejected ─► archived
```

Regras de transição (validar em `lifecycle.py`):
- **A IA só pode chegar até `draft`** (e recomendar via `status_recommendation`). Jamais
  setar `approved`.
- `approved` exige `require_permission(context, "rule.approve")`; `rejected` exige
  `rule.reject`. `viewer` nunca transiciona.
- `conflict_detected` é setado pelo **RAG Guardian** quando `requires_human_resolution=true`.
- Toda transição registra `write_audit_log` (`action="rule.<transição>"`) e mantém a
  `source_references` original da regra.
- Versionamento: ao substituir, a antiga vai para `replaced` e a nova referencia a anterior
  (`rule_versions`); `replaced`/`revoked`/`archived` são imutáveis depois.

## Campos relevantes da regra

`code` (ex.: `RULE-001`), `rule_text`, `rule_type`, `condition_text`, `result_text`,
`exception_text`, `status`, `confidence_score` (0–1), `quality_score` (0–100),
`source_chunk_ids[]` / `source_references[]`, `created_by`, `tenant_id`, `project_id`,
`meeting_id`.

## Checklist ao mexer no Rules Ledger

1. [ ] Transição validada contra a tabela acima (rejeitar transição inválida com `conflict`).
2. [ ] Mutação protegida por `require_permission` (approve/reject).
3. [ ] `write_audit_log` em toda mudança de status.
4. [ ] `source_references` preservadas (nunca perder a rastreabilidade).
5. [ ] IA nunca produz `approved`.
6. [ ] Conflito de RAG → `conflict_detected` + sinalização para humano.
