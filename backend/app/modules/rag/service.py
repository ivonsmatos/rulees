import hashlib
import json
import math
import re
from dataclasses import dataclass

from sqlalchemy import select, text as sql_text
from sqlalchemy.orm import Session

from app.modules.rag.embeddings_provider import embed_with_fallback
from app.modules.rag.models import SemanticEmbedding
from app.shared.enums import RuleStatus

EMBEDDING_DIMENSION = 64
EMBEDDING_MODEL = "rulees-hash-v1"
DIRECT_CONFLICT_THRESHOLD = 0.92
POSSIBLE_CONFLICT_THRESHOLD = 0.78
# Dimensão fixa suportada pelo índice nativo pgvector (ver migration 20260702_0016).
# Embeddings com outra dimensão (ex: provider OpenAI 1536-d) continuam funcionando
# via comparação Python (fallback), mas não são indexados nativamente.
NATIVE_INDEX_DIMENSION = EMBEDDING_DIMENSION


@dataclass(frozen=True)
class RagMatch:
    embedding: SemanticEmbedding
    similarity_score: float


@dataclass(frozen=True)
class RagGuardianResult:
    history_verified: bool
    result_type: str
    requires_human_resolution: bool
    summary: str
    retrieved_sources: list[dict]
    conflicts: list[dict]
    recommended_status: str


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[\wÀ-ÿ]+", text.lower())


def _deterministic_embed(text: str) -> list[float]:
    """Embedding local determinístico (hash de tokens). Usado como fallback e no
    provider padrão — mantém compatibilidade com o índice nativo pgvector."""
    vector = [0.0] * EMBEDDING_DIMENSION
    for token in _tokenize(text):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % EMBEDDING_DIMENSION
        weight = 1.0 + (digest[2] / 255)
        vector[index] += weight

    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]


def embed_text(text: str) -> list[float]:
    """Compatibilidade retroativa: sempre usa o embedding determinístico local."""
    return _deterministic_embed(text)


def embed_text_with_provider(text: str) -> tuple[list[float], str]:
    """
    Gera embedding usando o provider configurado em settings (deterministic |
    openai | ollama), com fallback automático para o determinístico em caso de erro.
    """
    return embed_with_fallback(text)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right))


def _loads_vector(raw_vector: str) -> list[float]:
    try:
        vector = json.loads(raw_vector)
    except json.JSONDecodeError:
        return []
    return [float(value) for value in vector] if isinstance(vector, list) else []


def _is_postgres(db: Session) -> bool:
    return db.bind is not None and db.bind.dialect.name == "postgresql"


def _to_pgvector_literal(vector: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in vector) + "]"


def upsert_embedding(
    db: Session,
    *,
    tenant_id: str,
    project_id: str,
    source_type: str,
    source_id: str,
    content: str,
    meeting_id: str | None = None,
) -> SemanticEmbedding:
    normalized_content = content.strip()
    vector, model_name = embed_text_with_provider(normalized_content)
    existing = db.scalar(
        select(SemanticEmbedding).where(
            SemanticEmbedding.tenant_id == tenant_id,
            SemanticEmbedding.source_type == source_type,
            SemanticEmbedding.source_id == source_id,
        )
    )
    if existing:
        existing.project_id = project_id
        existing.meeting_id = meeting_id
        existing.content = normalized_content
        existing.content_hash = content_hash(normalized_content)
        existing.embedding_model = model_name
        existing.embedding_dim = len(vector)
        existing.embedding_vector = json.dumps(vector)
        embedding = existing
    else:
        embedding = SemanticEmbedding(
            tenant_id=tenant_id,
            project_id=project_id,
            meeting_id=meeting_id,
            source_type=source_type,
            source_id=source_id,
            content_hash=content_hash(normalized_content),
            content=normalized_content,
            embedding_model=model_name,
            embedding_dim=len(vector),
            embedding_vector=json.dumps(vector),
        )
        db.add(embedding)

    # Popula o índice vetorial nativo do pgvector quando disponível (Postgres +
    # dimensão compatível com o índice fixo). Em SQLite/dimensões diferentes,
    # a busca cai automaticamente para o fallback Python (ver retrieve_similar).
    if _is_postgres(db) and len(vector) == NATIVE_INDEX_DIMENSION:
        db.flush()
        db.execute(
            sql_text(
                "UPDATE semantic_embeddings SET embedding_native = CAST(:vec AS vector) WHERE id = :id"
            ),
            {"vec": _to_pgvector_literal(vector), "id": embedding.id},
        )
    return embedding


def _retrieve_similar_native(
    db: Session,
    *,
    tenant_id: str,
    project_id: str,
    query_vector: list[float],
    limit: int,
    exclude_source_id: str | None,
) -> list[RagMatch] | None:
    """Busca vetorial nativa via operador pgvector `<=>` (distância de cosseno).
    Retorna None se a busca nativa não é aplicável (não-Postgres ou sem dados
    indexados), sinalizando para o chamador usar o fallback Python."""
    if not _is_postgres(db) or len(query_vector) != NATIVE_INDEX_DIMENSION:
        return None

    literal = _to_pgvector_literal(query_vector)
    exclude_clause = "AND source_id != :exclude_id" if exclude_source_id else ""
    params: dict = {
        "tenant_id": tenant_id,
        "project_id": project_id,
        "qvec": literal,
        "limit": limit,
    }
    if exclude_source_id:
        params["exclude_id"] = exclude_source_id

    rows = db.execute(
        sql_text(
            f"""
            SELECT id, 1 - (embedding_native <=> CAST(:qvec AS vector)) AS similarity_score
            FROM semantic_embeddings
            WHERE tenant_id = :tenant_id AND project_id = :project_id
              AND embedding_native IS NOT NULL
              {exclude_clause}
            ORDER BY embedding_native <=> CAST(:qvec AS vector)
            LIMIT :limit
            """
        ),
        params,
    ).fetchall()

    if not rows:
        return []

    ordered_ids = [row.id for row in rows]
    similarity_by_id = {row.id: float(row.similarity_score) for row in rows}
    embeddings = list(
        db.scalars(select(SemanticEmbedding).where(SemanticEmbedding.id.in_(ordered_ids)))
    )
    embeddings_by_id = {embedding.id: embedding for embedding in embeddings}
    matches = [
        RagMatch(embedding=embeddings_by_id[eid], similarity_score=similarity_by_id[eid])
        for eid in ordered_ids
        if eid in embeddings_by_id and similarity_by_id[eid] > 0
    ]
    return matches


def retrieve_similar(
    db: Session,
    *,
    tenant_id: str,
    project_id: str,
    query: str,
    limit: int = 8,
    exclude_source_id: str | None = None,
) -> list[RagMatch]:
    query_vector, _ = embed_text_with_provider(query)

    native_matches = _retrieve_similar_native(
        db,
        tenant_id=tenant_id,
        project_id=project_id,
        query_vector=query_vector,
        limit=limit,
        exclude_source_id=exclude_source_id,
    )
    if native_matches is not None:
        return native_matches

    embeddings = list(
        db.scalars(
            select(SemanticEmbedding).where(
                SemanticEmbedding.tenant_id == tenant_id,
                SemanticEmbedding.project_id == project_id,
            )
        )
    )
    matches: list[RagMatch] = []
    for embedding in embeddings:
        if exclude_source_id and embedding.source_id == exclude_source_id:
            continue
        similarity = cosine_similarity(query_vector, _loads_vector(embedding.embedding_vector))
        if similarity > 0:
            matches.append(RagMatch(embedding=embedding, similarity_score=similarity))
    return sorted(matches, key=lambda match: match.similarity_score, reverse=True)[:limit]


def rag_match_to_dict(match: RagMatch) -> dict:
    return {
        "source_type": match.embedding.source_type,
        "source_id": match.embedding.source_id,
        "meeting_id": match.embedding.meeting_id,
        "content": match.embedding.content,
        "similarity_score": round(match.similarity_score, 4),
        "created_at": match.embedding.created_at.isoformat(),
    }


def check_rule_conflicts(
    db: Session,
    *,
    tenant_id: str,
    project_id: str,
    rule_id: str,
    rule_text: str,
) -> RagGuardianResult:
    matches = retrieve_similar(
        db,
        tenant_id=tenant_id,
        project_id=project_id,
        query=rule_text,
        limit=5,
        exclude_source_id=rule_id,
    )
    retrieved_sources = [rag_match_to_dict(match) for match in matches]
    conflicts = [
        {
            **rag_match_to_dict(match),
            "conflict_type": "duplicate_rule"
            if match.similarity_score >= DIRECT_CONFLICT_THRESHOLD
            else "possible_overlap",
        }
        for match in matches
        if match.similarity_score >= POSSIBLE_CONFLICT_THRESHOLD
    ]

    if any(match.similarity_score >= DIRECT_CONFLICT_THRESHOLD for match in matches):
        return RagGuardianResult(
            history_verified=True,
            result_type="duplicate_rule",
            requires_human_resolution=True,
            summary="Regra candidata muito parecida com uma regra existente no projeto.",
            retrieved_sources=retrieved_sources,
            conflicts=conflicts,
            recommended_status=RuleStatus.conflict_detected,
        )

    if conflicts:
        return RagGuardianResult(
            history_verified=True,
            result_type="possible_conflict",
            requires_human_resolution=True,
            summary="Regra candidata possui sobreposição semântica com memória do projeto.",
            retrieved_sources=retrieved_sources,
            conflicts=conflicts,
            recommended_status=RuleStatus.conflict_detected,
        )

    return RagGuardianResult(
        history_verified=True,
        result_type="no_conflict",
        requires_human_resolution=False,
        summary="Nenhum conflito relevante encontrado na memória do projeto.",
        retrieved_sources=retrieved_sources,
        conflicts=[],
        recommended_status=RuleStatus.needs_review,
    )
