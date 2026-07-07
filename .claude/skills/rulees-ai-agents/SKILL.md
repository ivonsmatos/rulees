---
name: rulees-ai-agents
description: >
  Contrato de saída dos agentes de IA do Rulees e regras anti-alucinação. Use ao
  implementar/alterar o pipeline de IA (LangGraph), os agentes Scribe, Observer,
  RAG Guardian, Inquisitor e Decision, a normalização de transcrição, extração de
  regras candidatas, detecção de conflito via RAG, geração de perguntas/decisões,
  ou qualquer schema JSON de entrada/saída de agente. Garante envelope padrão,
  confidence/quality scores, source_references e controle humano.
---

# Rulees — Agentes de IA e Contrato de Saída

Fonte: `documentos/Rulees - JSON Schema.docx` + `documentos/Arquitetura de IA.docx`.
Local de implementação: `backend/app/modules/ai_agents/` (orquestração LangGraph).
Hoje a IA roda como **heurística local determinística**; ao plugar LLM real, manter
exatamente este contrato.

## Agentes do sistema

| Agente | Papel (`agent_role`) | Função |
|---|---|---|
| **Scribe** | `transcript_normalizer` | Normaliza transcrição bruta do STT; preserva `raw_text`. Não cria regra. |
| **Observer** | `business_rule_extractor` | Extrai regras candidatas, riscos, dependências, requisitos. |
| **RAG Guardian** | `historical_consistency_checker` | Consulta embeddings (filtrado por tenant+project) e detecta conflito/duplicidade. |
| **Inquisitor** | `gap_detector` | Identifica lacunas e gera perguntas inteligentes. |
| **Decision** | (decisor) | Consolida e recomenda status; nunca aprova sozinho. |

## Envelope padrão (TODA resposta de agente)

```json
{
  "schema_version": "1.0",
  "agent_name": "Observer",
  "agent_role": "business_rule_extractor",
  "run_id": "run_observer_001",
  "tenant_id": "tenant_001",
  "project_id": "project_001",
  "meeting_id": "meeting_001",
  "input_reference": { "source_type": "transcript_chunk", "source_ids": ["chunk_001"] },
  "status": "success",
  "confidence_score": 0.91,
  "warnings": [],
  "errors": [],
  "metadata": { "model": "...", "prompt_version": "observer_v1.0", "latency_ms": 1800 },
  "output": { }
}
```

Campos obrigatórios: `schema_version, agent_name, agent_role, run_id, tenant_id,
project_id, meeting_id, status, output`. `input_reference` rastreia a origem.

## Status permitidos (`status`)

| Status | Quando usar |
|---|---|
| `success` | Rodou e produziu resultado válido. |
| `partial_success` | Produziu algo, mas com warnings/limitações. |
| `no_relevant_content` | Rodou mas não havia conteúdo relevante (ex.: Observer sem regra). |
| `failed` | Erro impediu o resultado (preencher `errors`). |
| `skipped` | Não rodou de propósito (ex.: RAG sem regra candidata). |

## Tipos globais reutilizáveis

- **confidence_score**: escala `0.0–1.0`. (0–0.39 baixa · 0.40–0.69 moderada · 0.70–0.89 boa · 0.90–1.0 alta)
- **quality_score**: escala `0–100`. (0–39 fraco · 40–59 insuficiente · 60–79 aceitável · 80–100 bom)
- **source_reference**: `{ source_type, source_id, start_time, end_time, quoted_text }`
- **warning**: `{ code, message, severity }` — severidade: `low|medium|high|critical`
- **error**: `{ code, message, recoverable, details }`

## Regras anti-alucinação (HARD — nunca violar)

1. **IA não aprova nada.** Toda regra criada por IA sai com `status_recommendation`
   **diferente de `approved`** (tipicamente `draft`). Aprovação é só humana (`rule.approve`).
2. **Toda `business_rule` tem `rule_text` e `source_references`.** Sem fonte → não emitir.
3. **Scribe não inventa.** Preserva `raw_text`; não adiciona valor, prazo ou condição
   inexistente; correções relevantes vão em `corrections`.
4. **RAG isolado por tenant.** `filters_applied.tenant_id` (e `project_id` p/ contexto de
   projeto) são obrigatórios. Se o RAG falhar, `history_verified = false`.
5. **Conflito exige humano.** Se houver conflito, `requires_human_resolution = true` e
   `recommended_status = "conflict_detected"`.
6. **Sem regra → `no_relevant_content`** (não forçar saída).

## Saídas por agente (resumo)

- **Scribe.output**: `chunk_id, raw_text, normalized_text, language, speaker_label,
  start_time, end_time, corrections[], semantic_segments[]`.
- **Observer.output**: `detected_items[]` (cada item com `item_type` e `rule_candidate`),
  `risks[]`, `dependencies[]`. Tipos de regra: `eligibility, calculation, permission,
  restriction, deadline, exception, workflow, approval, notification, integration,
  compliance, pricing, data_validation, business_policy, operational_rule`.
- **RAG Guardian.output**: `history_verified, result_type, requires_human_resolution,
  summary, retrieved_sources[], conflicts[], recommended_status`. `result_type`:
  `no_conflict, possible_conflict, direct_conflict, duplicate_rule, partial_overlap,
  outdated_rule, requires_human_review`.
- **Inquisitor.output**: `questions[]` (cada uma com `question_text, reason, gap_type,
  priority, related_rule_id, source_references, expected_answer_type`).

## Orquestração (LangGraph)

- **Fluxo ao vivo** (durante a reunião): Scribe → Observer → (regra candidata) → emite
  eventos WebSocket `ai.rule.detected` / `ai.question.suggested` / `ai.decision.detected`.
- **Fluxo pós-reunião**: reprocessa chunks, roda RAG Guardian para conflitos, consolida
  no Rules Ledger (ver skill `rulees-rules-ledger`).
- Estado compartilhado carrega sempre `tenant_id, project_id, meeting_id, run_id`.
- Registrar cada execução em `agent_runs` (rastreabilidade/observabilidade + billing por
  `agent_runs`/`llm_input_tokens`/`llm_output_tokens`).
