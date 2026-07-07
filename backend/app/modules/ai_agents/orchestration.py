"""
Orquestração multiagente via LangGraph.

Implementa o pipeline de classificação Scribe -> Observer -> Rule Quality ->
Inquisitor -> Decision como um grafo de estados real (`langgraph.graph.StateGraph`),
reaproveitando as mesmas funções determinísticas já usadas no pipeline de tempo
real (`app/modules/rules_ledger/service.py`, `app/modules/questions/service.py`,
`app/modules/decisions/service.py`) — sem duplicar regra de negócio.

Uso:
    from app.modules.ai_agents.orchestration import analyze_transcript_text
    result = analyze_transcript_text("Quando o cliente...")
    # result["is_rule_candidate"], result["quality_details"], result["engine"], ...

Se o pacote `langgraph` não estiver instalado, o pipeline cai automaticamente
para uma execução sequencial equivalente (mesmas funções, mesma ordem),
garantindo que o comportamento nunca quebre por ausência da dependência opcional.
"""

from __future__ import annotations

from typing import Any, TypedDict

from app.modules.decisions.service import should_detect_decision
from app.modules.questions.service import should_suggest_question
from app.modules.rules_ledger.service import (
    calculate_rule_quality_details,
    looks_like_rule,
    normalize_text,
)

try:
    from langgraph.graph import END, StateGraph

    _HAS_LANGGRAPH = True
except ImportError:  # pragma: no cover - fallback quando langgraph não instalado
    StateGraph = None  # type: ignore[assignment]
    END = "__end__"
    _HAS_LANGGRAPH = False


class PipelineState(TypedDict, total=False):
    raw_text: str
    normalized_text: str
    is_rule_candidate: bool
    quality_details: dict[str, Any]
    is_question_candidate: bool
    is_decision_candidate: bool
    engine: str


def _node_normalize(state: PipelineState) -> dict:
    return {"normalized_text": normalize_text(state["raw_text"])}


def _node_classify_rule(state: PipelineState) -> dict:
    text = state["normalized_text"]
    is_rule = looks_like_rule(text)
    quality_details: dict[str, Any] = {}
    if is_rule:
        quality_details = calculate_rule_quality_details(rule_text=text, confidence_score=0.76)
    return {"is_rule_candidate": is_rule, "quality_details": quality_details}


def _node_classify_question(state: PipelineState) -> dict:
    return {"is_question_candidate": should_suggest_question(state["normalized_text"])}


def _node_classify_decision(state: PipelineState) -> dict:
    return {"is_decision_candidate": should_detect_decision(state["normalized_text"])}


def build_transcript_analysis_graph():
    """Compila o grafo LangGraph: normalize -> classify_rule -> classify_question -> classify_decision."""
    if not _HAS_LANGGRAPH:
        return None

    graph = StateGraph(PipelineState)
    graph.add_node("normalize", _node_normalize)
    graph.add_node("classify_rule", _node_classify_rule)
    graph.add_node("classify_question", _node_classify_question)
    graph.add_node("classify_decision", _node_classify_decision)

    graph.set_entry_point("normalize")
    graph.add_edge("normalize", "classify_rule")
    graph.add_edge("classify_rule", "classify_question")
    graph.add_edge("classify_question", "classify_decision")
    graph.add_edge("classify_decision", END)

    return graph.compile()


_compiled_graph: Any = None
_compiled_graph_initialized = False


def _get_compiled_graph():
    global _compiled_graph, _compiled_graph_initialized
    if not _compiled_graph_initialized:
        _compiled_graph = build_transcript_analysis_graph()
        _compiled_graph_initialized = True
    return _compiled_graph


def is_langgraph_available() -> bool:
    return _HAS_LANGGRAPH


def analyze_transcript_text(raw_text: str) -> PipelineState:
    """
    Executa o pipeline de classificação sobre um texto de transcrição.

    Usa o motor LangGraph (StateGraph compilado) quando o pacote está instalado;
    cai para uma execução sequencial equivalente caso contrário — mesma lógica,
    mesma ordem de nós, apenas sem o motor de grafo.
    """
    compiled = _get_compiled_graph()
    initial_state: PipelineState = {"raw_text": raw_text}

    if compiled is not None:
        result = compiled.invoke(initial_state)
        result["engine"] = "langgraph"
        return result

    state: dict[str, Any] = dict(initial_state)
    state.update(_node_normalize(state))  # type: ignore[arg-type]
    state.update(_node_classify_rule(state))  # type: ignore[arg-type]
    state.update(_node_classify_question(state))  # type: ignore[arg-type]
    state.update(_node_classify_decision(state))  # type: ignore[arg-type]
    state["engine"] = "sequential_fallback"
    return state  # type: ignore[return-value]
