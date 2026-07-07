# Rulees — Checklist de Próximos Passos até o Lançamento

Gerado em 2026-07-07 a partir do confronto entre a documentação (`documentos/`,
em especial "Checklist Final de Lançamento do MVP" e "Critérios de Aceite do MVP")
e o estado real do código.

## Diagnóstico resumido

O esqueleto do produto está completo e os 23 testes de backend passam. O fluxo
principal (conta → tenant → projeto → reunião → consentimento → WebSocket →
transcrição → detecção → aprovação humana → documento → PDF → auditoria) funciona
de ponta a ponta **em ambiente de desenvolvimento com heurísticas locais**.

Porém, `docs/PROJECT_COMPLETION_BACKLOG.md` marca itens como concluídos que na
prática são stubs ou implementações mínimas. O que separa o estado atual de um
beta lançável, segundo os próprios documentos de visão:

| Área | Estado real verificado no código |
|---|---|
| IA dos agentes | Nós do LangGraph são heurísticas por palavra-chave (`looks_like_rule` etc.). `ollama_adapter.py` existe mas **não está plugado** no grafo. `LLM_PROVIDER=openai` é aceito nas settings mas não há adapter OpenAI/Anthropic para agentes. |
| STT | Default `mock`. Adapter Deepgram coberto só por testes de contrato; nunca validado com áudio real. |
| PDF | `documents/pdf.py` escreve bytes PDF 1.4 à mão — sem layout, tabelas ou branding. |
| Observabilidade | Sentry e OpenTelemetry são **stubs de status** (nenhum SDK em `requirements.txt`). Sem métricas nem alertas reais. |
| Worker/fila | Redis aparece só no health check. Não há worker (Arq) — todo processamento é inline na request/WS. |
| Billing | Um único endpoint `GET /billing/status`. Sem upgrade self-service, sem Stripe, sem custo real por provider. |
| Frontend | `App.tsx` monolítico (103 KB), sem router, sem PWA (manifest/service worker), sem testes. |
| CI/CD | CI roda só pytest + build do frontend. Sem lint, secret scan, deploy staging/prod, migrations no pipeline ou rollback. |
| Infra | Sem ambientes staging/produção provisionados, sem storage real (S3), sem backup, sem HTTPS/WSS reais. |
| Módulos P3 | `sso`, `scim`, `byok`, `marketplace`, `api_keys` são implementações finas de demonstração (ok — fora do escopo MVP). |

Regra final do documento de lançamento: *"Se o fluxo reunião → regra → aprovação
→ documento → exportação não estiver funcionando com segurança, ainda não é
beta. É protótipo."* Hoje o projeto é um protótipo avançado e bem estruturado.

---

## Fase 1 — Núcleo de valor real (bloqueia tudo)

A promessa do produto ("detectar regras em reuniões reais") não se sustenta com
heurísticas de palavra-chave sobre fala espontânea.

- [x] Plugar LLM real nos nós do pipeline ao vivo (Observer/Inquisitor/Decision
      combinados em `classify_transcript_text`), mantendo o envelope schema 1.0,
      `source_references` obrigatórios e fallback heurístico automático em caso
      de falha/timeout. Ver `backend/app/modules/ai_agents/llm_classifier.py`.
- [x] Criar adapter LLM para provider cloud (OpenAI) além do Ollama; `LLM_PROVIDER`
      liga de fato à classificação ao vivo. Anthropic ainda não tem adapter dedicado.
- [x] Prompts versionados (`prompt_version` registrado em cada `agent_run`),
      exigido pelo checklist de schemas de IA (doc §15).
- [x] Fallback: falha do LLM cai para heurística e marca warning no run —
      "falha de IA não derruba reunião" (doc §42). Inclui checagem anti-alucinação
      que descarta campos extraídos pelo LLM não fundamentados na transcrição real.
- [ ] Validar STT Deepgram com áudio real pt-BR: latência de partial/final,
      diarização, custo por minuto. Configurar `DEEPGRAM_API_KEY` em ambiente real.
- [ ] Testar o fluxo reunião real de 15–30 min de ponta a ponta com STT + LLM
      reais (meta doc §41: regra clara em ≤20–30 s).

## Fase 2 — Robustez do produto

- [x] Substituir o PDF artesanal por biblioteca real (reportlab):
      título, data, projeto, status, regras com IDs, seções, branding Rulees
      (doc §22). Paginação real (corrige truncamento silencioso em 38 linhas),
      escape XML de conteúdo de regra/transcrição. 4 testes novos.
- [x] ~~Worker assíncrono (Arq + Redis)~~ — **avaliado e adiado deliberadamente**
      pelo arquiteto (Plan agent, 2026-07-07). Nenhum job atual é pesado o
      suficiente para justificar fila: PDF/Excel são só manipulação de
      string/bytes em memória (sub-segundo); export jira/confluence hoje só
      monta um payload JSON local, sem chamada HTTP externa real. Introduzir
      Arq agora é infraestrutura nova (processo extra, retry/dead-letter, CI
      sem Redis hoje) para zero ganho medido. **Gatilho objetivo de
      reavaliação:** (a) quando o pós-processamento de reunião (reconciliação
      de regras, geração de documento, backfill de embeddings) passar de
      segundos para minutos em teste real; ou (b) quando `create_export_job`
      (jira/confluence) passar a fazer chamada HTTP real para API externa —
      aí sim retry/fila viram a ferramenta certa.
- [x] Feature flags para desligar IA, RAG, geração de documento e exportação
      (exigência de rollback, doc §43). `ai_enabled`/`rag_enabled`/
      `document_generation_enabled`/`export_enabled` em
      `backend/app/core/settings.py`, com gate nos 3 endpoints de export
      (incluindo `signed_export_url`, que tinha ficado sem o gate).
- [ ] Refatorar frontend: quebrar `App.tsx` em `features/` por domínio com
      router; manter identidade visual (skill `rulees-frontend`).
- [ ] PWA mínimo: manifest, service worker, ícones — a arquitetura de frontend
      documentada é "PWA".
- [ ] Testes de frontend (ao menos smoke dos fluxos críticos: login, criar
      reunião, consentimento, aprovar regra, exportar PDF).
- [ ] Billing: fluxo de upgrade/downgrade simples (mesmo que manual/por contato
      no beta) + registro de custo real por provider (STT min, LLM tokens,
      embeddings) nos `usage_events` (doc §27).

## Achados de revisão de arquitetura (2026-07-07, não previstos no levantamento inicial)

- [x] Chamada síncrona bloqueante no event loop do WebSocket: `check_rule_conflicts`/
      `upsert_embedding` em `realtime/websocket.py` fazem HTTP síncrono via
      `embed_with_fallback` quando `embedding_provider` é openai/ollama, travando
      conexões concorrentes. Corrigido com `asyncio.to_thread` (mesmo padrão do
      `llm_classifier.py`).
- [x] Handler do WebSocket só capturava `WebSocketDisconnect` — qualquer outra
      exceção derrubava a conexão sem emitir `error.validation`. Corrigido:
      `except Exception` faz rollback + emite `error.validation` + continua o loop.
- [x] Reunião ficava presa para sempre em `MeetingStatus.processing`. Confirmado
      contra `documentos/Fluxo Completo da Reunião.docx` que a transição correta
      é `processing → processing_completed`; `complete_meeting_processing()` em
      `meetings/lifecycle.py` chamada em `meetings/router.py::finish` e no
      handler `meeting.stop` do WebSocket.
- [x] `signed_export_url` (`documents/router.py`) gerava PDF/Excel sem checar
      `export_enabled` — kill switch furado por essa rota. Corrigido junto com
      os outros 2 gates de export.

Suite completa: **40/40 testes passando** em `main` (23 originais + 9 do
classificador LLM + 4 do PDF + 3 de export flags + 1 de meeting-stop).

## Fase 3 — Operação e infraestrutura

- [ ] Sentry real (SDK instalado, DSN por ambiente) — hoje é stub.
- [ ] OpenTelemetry real ou, no mínimo, métricas básicas expostas — hoje é stub.
- [ ] Alertas mínimos: API/banco fora, falha STT/IA em massa, tentativa
      cross-tenant, custo anormal (doc §29).
- [ ] Storage real privado (S3/R2/compatível) com URL assinada e expiração —
      validar que PDF nunca fica público (NO-GO doc §22).
- [ ] Provisionar staging e produção separados (banco, Redis, storage, secrets
      por ambiente) com HTTPS/WSS (doc §30).
- [ ] CI: adicionar lint (backend + `npm run lint`), secret scan, build de
      imagem Docker rastreável por commit SHA.
- [ ] CD: deploy automático em staging; produção com aprovação manual;
      migrations Alembic rodando em staging antes de produção (doc §31).
- [ ] Backup automático do banco + teste de restore documentado (doc §32).
- [ ] Plano de rollback escrito (versão anterior reimplantável, doc §43).
- [ ] Runbooks: WebSocket, STT, IA, RAG, PDF, billing, cross-tenant (doc §44).

## Fase 4 — Validação (Go/No-Go técnico)

- [ ] Executar o checklist E2E obrigatório (doc §34) em **staging**: dos
      "Criar usuário Admin" até "Ver usage_events" — 19 passos.
- [ ] Repetir os testes cross-tenant em staging com dados reais (doc §7.1 —
      qualquer falha = NO-GO).
- [ ] Dataset mínimo de avaliação da IA: casos com regra clara, sem regra,
      ambíguos, com decisão, com conflito, com prompt injection (doc §40).
- [ ] Medir metas de qualidade: ≥70% das regras claras detectadas; taxa de JSON
      válido; falso positivo aceitável (doc Critérios §9).
- [ ] Medir metas de performance: partial ≤3 s, final ≤8 s, regra ≤20 s,
      documento ≤2 min, PDF ≤30 s (doc Critérios §11).
- [ ] Processar ≥3 reuniões de teste completas com sucesso em staging
      (Definição de Pronto, doc Critérios §17).
- [ ] Checklist anti-alucinação (doc §16): regra sem evidência não aprova, IA
      nunca retorna `approved`, prompt injection ignorado.

## Fase 5 — Lançamento do beta fechado

- [ ] Política de privacidade beta + termo de beta (LGPD, doc §25).
- [ ] Processo manual de exclusão/anonimização de dados documentado.
- [ ] Onboarding: guia de primeiros passos, primeira reunião, FAQ de microfone/
      consentimento/Rules Ledger (doc §35).
- [ ] Canal e responsável de suporte + severidades P0–P3 definidas.
- [ ] Dados de demonstração: tenant/projeto/reunião/documento/PDF demo +
      roteiro de demo testado (doc §39).
- [ ] Landing page ou página de espera + one-pager + oferta beta (doc §37).
- [ ] Lista de 5–10 empresas beta qualificadas + formulário de feedback +
      métricas de sucesso do beta (doc §36 e §50).
- [ ] Sessão formal de Go/No-Go técnico, de produto e comercial (docs §45–47).

---

## Fora do escopo até o beta (não fazer agora)

Jira/Confluence/Azure DevOps reais, SSO/SAML, SCIM, marketplace, API pública,
BI avançado, BYOK completo, deployment privado, mobile nativo — os documentos
explicitamente os excluem do MVP. Os stubs existentes podem ficar como estão.

## Ação de higiene sugerida

Revisar `docs/PROJECT_COMPLETION_BACKLOG.md`: os blocos P1/P2/P3 e vários itens
de P0 (OpenTelemetry, Sentry, "PDF com layout robusto", "custo estimado por
STT/LLM") estão marcados `[x]` mas correspondem a stubs — isso mascara o
trabalho restante e pode induzir decisões erradas de lançamento.
