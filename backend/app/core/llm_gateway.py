# core/llm_gateway.py — SE-58, LLM_Staffing_Fallback_Plan: Multi-provider, role routing, health, LKS/Blackout.
# Phase 3-1: skeleton. Engines do NOT call this; worker/orchestration calls it. No DB inside engines.

from __future__ import annotations

from typing import Any

# Role constants (SE-58)
ROLE_JCS = "JCS"
ROLE_STRATCOM = "STRATCOM"
ROLE_SRC = "SRC"
ROLE_STRIKE = "Strike"
ROLE_RESERVE = "Reserve"


def request_llm(
    role: str,
    task_type: str,
    payload: dict,
    *,
    providers: list[str] | None = None,
    max_latency_ms: int = 30_000,
) -> dict[str, Any]:
    """
    Skeleton: Multi-provider request. Returns {ok, provider_used, model_used, latency_ms, result, error}.
    Real impl: Primary → Secondary → Tertiary; on full failure record incident and return LKS.
    """
    return {
        "ok": False,
        "provider_used": None,
        "model_used": None,
        "latency_ms": 0,
        "result": None,
        "error": "LLM gateway not implemented (skeleton)",
    }


def get_health() -> dict[str, Any]:
    """Skeleton: Provider-wise health (latency, error_rate, last_ok_at)."""
    return {"providers": {}, "status": "unknown"}


def get_lks(db) -> dict[str, Any]:
    """Last-Known Strategy: load from DB (system_config)."""
    from backend.app.core import config_service
    out = config_service.get_config(db, "lks_last_known_strategy")
    return out if isinstance(out, dict) else {}


def record_lks(db, lks: dict[str, Any]) -> None:
    """Persist LKS to DB for blackout recovery."""
    from backend.app.core import config_service
    config_service.set_config(db, "lks_last_known_strategy", lks, "llm_gateway")


def on_blackout(db) -> None:
    """On full LLM failure: record incident_log (Phase 3-2)."""
    from backend.app.core.incident_repo import create_incident
    create_incident(db, "WARNING", "LLM_BLACKOUT", "All LLM providers failed; LKS mode.", "llm_status")
