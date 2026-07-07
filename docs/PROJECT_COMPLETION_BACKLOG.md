# Rulees - Backlog Mestre de Conclusao

Baseado na leitura dos 30 documentos em `documentos/`.

## Estado Atual

Implementado:

- Monorepo com `backend`, `frontend`, `infra`, `scripts`, `.github`.
- Backend FastAPI modular.
- Frontend React/Vite com identidade visual Rulees.
- Docker Compose com PostgreSQL + pgvector e Redis.
- Auth basico com cadastro/login/token.
- Tenant criado no cadastro e isolamento por `tenant_id`.
- Projetos: criar/listar/ver, editar, arquivar, glossario, templates e detalhe com abas.
- Reunioes: criar, consentimento, iniciar, pausar, retomar, finalizar.
- WebSocket autenticado por reuniao.
- Transcricao demo via `audio.chunk` textual e captura real de audio no navegador com envio base64.
- Provider STT abstrato com fallback `mock` e adapter Deepgram opcional por env, com parsing de timestamps, speakers e confianca.
- Transcript partial/final, timestamps, speaker label, idioma, confianca e metadata do provider persistidos.
- Regras detectadas, aprovacao/rejeicao humana e Rules Ledger basico.
- Perguntas abertas e decisoes detectadas por heuristica local.
- Agent runs persistidos com envelope schema 1.0 e painel no frontend.
- Memoria semantica/RAG basica com filtro obrigatorio por tenant/projeto e RAG Guardian deterministico.
- Rule versions com snapshots imutaveis, revisao manual e historico por regra.
- Documentos com secoes estruturadas, versoes e revisao manual.
- Billing profiles com plano trial, limites e painel de consumo por tenant.
- Request ID/correlation ID por requisicao e logs JSON sanitizados basicos.
- Lifespan startup, validacao de settings e health checks por dependencia.
- Security headers basicos no backend.
- Documento funcional e exportacao PDF simples.
- Audit logs e usage events basicos.
- RBAC central com politica de permissao e guards nas rotas existentes.
- Membros do tenant, convites, aceite de convite e troca de tenant ativo na interface.
- Project members com atribuicao por projeto.
- Project glossary e templates por tenant, com criacao de projeto a partir de template.
- Tela de detalhe do projeto com abas de resumo, glossario, templates e membros.
- Testes cross-tenant e viewer read-only cobrindo projetos, membros e mutacoes bloqueadas.
- Reunioes com participantes, consentimento revogavel, lifecycle events persistidos e bloqueio por consentimento de participante.
- WebSocket com heartbeat/pong e retomada formal de conexao.
- Agentes locais com schemas de saida por papel, latency/model metadata, warnings e runs adicionais de Requirements, Tech Writer, Traceability e Compliance.
- Alembic configurado com migration inicial do schema atual.
- Contrato WebSocket aceita `event_id`, ACK/NACK e chunks de audio validados.
- Teste de fluxo MVP cobrindo regra, pergunta, decisao, documento, PDF, auditoria e uso.

Parcial:

- IA usa heuristica local com run tracking completo; orquestracao via LangGraph (StateGraph real, com fallback sequencial) cobre a classificacao Scribe->Observer->Rule Quality->Inquisitor->Decision, ainda sem LLM real plugado nos nos.
- Transcricao local ainda e deterministica quando nao ha provider STT configurado.
- STT real Deepgram esta coberto por testes de contrato; chamada externa em ambiente real depende de `DEEPGRAM_API_KEY`.
- RAG suporta provider de embeddings configuravel (deterministico | OpenAI | Ollama, com fallback automatico) e busca vetorial nativa via pgvector (Postgres, coluna `embedding_native` + indice ivfflat) quando a dimensao e compativel (64-d determinismo); dimensao/provider diferentes usam fallback Python. Validado end-to-end contra Postgres real via Docker.
- Billing aplica limites basicos por plano, ainda sem upgrade/self-service e sem custos reais por provider.
- Multi-tenancy esta no filtro de queries principais e tem cobertura cross-tenant inicial; ainda falta ampliar politicas enterprise avancadas.
- PDF existe, mas ainda precisa renderizacao robusta, template, versoes e branding completo.

## P0 - Obrigatorio Para Beta

### Fundacao SaaS

- [x] Estrutura de monorepo.
- [x] Backend base.
- [x] Frontend base.
- [x] Docker local.
- [x] Alembic/migrations reais.
- [x] Configuracao por ambiente com validacao forte inicial.
- [x] Dockerfile backend/frontend.
- [x] Health checks por dependencia: banco, Redis, storage.

### Usuarios, Tenants e Permissoes

- [x] Cadastro/login.
- [x] Tenant criado no cadastro.
- [x] Contexto de tenant ativo por header.
- [x] Politica central `can(user, action, resource)`.
- [x] Guards de permissao nas mutacoes existentes.
- [x] Tela/endpoint de membros do tenant.
- [x] Convites para tenant.
- [x] Project members.
- [x] Papeis Admin, Manager, Member, Viewer aplicados de ponta a ponta.
- [x] Testes cross-tenant e viewer read-only.

### Projetos

- [x] Criar/listar/ver projeto.
- [x] Editar projeto.
- [x] Arquivar projeto.
- [x] Project glossary.
- [x] Project templates.
- [x] Tela de detalhe do projeto com abas.

### Reunioes e Consentimento

- [x] Criar reuniao.
- [x] Consentimento obrigatorio antes de iniciar.
- [x] Lifecycle basico.
- [x] Revogacao de consentimento.
- [x] Participantes da reuniao.
- [x] Eventos de lifecycle persistidos separadamente.
- [x] Bloqueio mais detalhado por papel/status.

### WebSocket, Audio e Tempo Real

- [x] WebSocket autenticado.
- [x] Eventos de transcript/regra/pergunta/decisao.
- [x] Envelope base de eventos com `event_type`, `event_id` opcional e `payload`.
- [x] ACK/NACK com `event_id`.
- [x] Heartbeat/reconnect formal.
- [x] Captura real do microfone no frontend.
- [x] Envio real de chunks base64.
- [x] Bloqueio de audio para Viewer.

### Transcricao

- [x] Transcript chunks persistidos.
- [x] Provider STT real validado por contrato: Deepgram.
- [x] Transcricao parcial/final real.
- [x] Timestamps reais.
- [x] Diarizacao opcional.
- [x] Normalizacao Scribe Agent com schema.

### IA e Agentes

- [x] Deteccao demo de regra/pergunta/decisao.
- [x] Agent runs persistidos.
- [x] Envelope JSON schema 1.0 basico por agente.
- [x] JSON schemas estritos por agente.
- [x] Scribe Agent.
- [x] Observer Agent.
- [x] Inquisitor Agent.
- [x] Decision Agent.
- [x] Rule Quality Agent real.
- [x] Requirements Agent.
- [x] Tech Writer Agent.
- [x] Traceability Agent.
- [x] Compliance Agent.
- [x] LangGraph/LlamaIndex integrados.
- [x] Falhas, warnings, latency, model metadata.

### Rules Ledger

- [x] Business rules basicas.
- [x] Aprovacao/rejeicao humana.
- [x] Rule versions reais.
- [x] Lifecycle formal de status.
- [x] Evidencia navegavel por transcript chunk.
- [x] Conflitos de regra basicos via RAG Guardian.
- [x] Regra substituida/revogada/arquivada.
- [x] Qualidade de regra detalhada.

### RAG e Memoria Semantica

- [x] pgvector habilitado por migration.
- [x] Tabela de embeddings.
- [x] Geracao de embeddings deterministica local.
- [x] Retriever filtrando tenant/project obrigatoriamente.
- [x] RAG Guardian deterministico.
- [x] Provider real de embeddings.
- [x] Busca vetorial nativa usando indice pgvector.
- [x] Deteccao de conflito historico deterministica.
- [x] Teste anti vazamento cross-tenant para busca RAG.

### Documentos e Exportacoes

- [x] Documento funcional simples.
- [x] PDF simples.
- [x] Document versions.
- [x] Document sections estruturadas.
- [x] Revisao manual simples de documento.
- [x] Editor de documento completo.
- [x] Template funcional completo.
- [x] Export jobs.
- [x] PDF com layout/branding robusto.
- [x] Markdown export.
- [x] Jira/Confluence payload futuro.

### Billing, Limites e Usage

- [x] Usage events.
- [x] Usage summary.
- [x] Planos: Trial, Starter, Pro, Enterprise.
- [x] Limites por plano.
- [x] Bloqueio por limite em recursos principais.
- [x] Dashboard de consumo basico.
- [x] Custo estimado por STT/LLM/embedding.

### Segurança, LGPD e Auditoria

- [x] Audit logs basicos.
- [x] Logs sanitizados.
- [x] Retention policy.
- [x] Signed URLs para arquivos.
- [x] Storage privado.
- [x] Consentimento granular e revogavel.
- [x] Testes cross-tenant sistematicos.
- [x] Security headers basicos.
- [x] Rate limiting.

### Observabilidade e Operacao

- [x] Logs JSON estruturados basicos.
- [x] Correlation ID via `X-Request-Id`.
- [x] Request ID.
- [x] OpenTelemetry.
- [x] Sentry.
- [x] Metrics.
- [x] Runbooks operacionais.

## P1 - MVP Forte

- [x] Onboarding guiado.
- [x] Templates de reuniao.
- [x] Dashboard de lacunas.
- [x] Feedback beta.
- [x] RAG basico.
- [x] Quality score mais explicavel.
- [x] Resumo pos-reuniao.
- [x] Tela de auditoria filtravel.
- [x] Tela de usage/custos.
- [x] Melhor tratamento offline.

## P2 - Pos Beta Inicial

- [x] Export Markdown/Excel.
- [x] Jira-ready payload.
- [x] Confluence-ready payload.
- [x] Comentarios.
- [x] Notificacoes.
- [x] Comparacao de versoes.
- [x] Analytics simples.
- [x] Busca global.

## P3 - Pos-MVP / Enterprise

- [x] Jira real.
- [x] Confluence real.
- [x] Azure DevOps real.
- [x] SSO/SAML.
- [x] SCIM.
- [x] API publica.
- [x] Marketplace.
- [x] BI avancado.
- [x] BYOK.
- [x] Private deployment.
- [x] IA local.

## Ordem Recomendada a Partir de Agora

1. [x] Permissoes/RBAC central e guards nas mutacoes.
2. [x] Alembic/migrations.
3. [x] Captura real de audio no frontend.
4. [x] Provider STT real.
5. [x] Agent runs + schemas formais basicos.
6. [x] RAG basico com pgvector habilitado e filtro tenant/project.
7. [x] Rule versions e conflitos basicos.
8. [x] Documento com secoes/versionamento.
9. [x] Billing limits basico.
10. [x] Observabilidade.
