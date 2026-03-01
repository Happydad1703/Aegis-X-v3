# core/snapshot_keys.py — SSOT: 허용 snapshot_key 화이트리스트 (SE-44, Phase 0-1 정본)
# API는 이 목록 밖의 키를 절대 반환하지 않음. 카탈로그·코드 중복 정의 금지.

from __future__ import annotations

# Phase 0-1 필수 6종 + Phase 2 확장 (단일 소스)
ALLOWED_SNAPSHOT_KEYS = frozenset({
    "engine_heartbeat",
    "comm_health",
    "regime_current",
    "operation_mode",
    "llm_status",
    "risk_guard",
    "allocation_matrix",
    "fleet_budget_snapshot",
    "core_force_state",
})


def is_allowed_snapshot_key(key: str) -> bool:
    """화이트리스트에 있는 키만 허용."""
    return key in ALLOWED_SNAPSHOT_KEYS


def get_required_snapshot_keys_for_cycle() -> tuple[str, ...]:
    """엔진 1사이클에서 반드시 기록해야 할 키 목록 (순서 무관)."""
    return tuple(ALLOWED_SNAPSHOT_KEYS)
