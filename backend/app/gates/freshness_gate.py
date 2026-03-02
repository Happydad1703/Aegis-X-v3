# gates/freshness_gate.py — SE-50: Freshness Gate. regime_current, allocation_matrix 최신 ≤ MAX_STALE_SEC.

from __future__ import annotations

from datetime import datetime, timezone

MAX_STALE_SEC = 120


def run_freshness_gate(db) -> tuple[bool, str]:
    """
    DB engine_snapshot에서 regime_current, allocation_matrix generated_at 확인.
    둘 중 하나라도 MAX_STALE_SEC 초과 시 차단.
    Returns: (allow, message).
    """
    try:
        from backend.app.core.snapshot_repo import get_latest_snapshot_sync
    except Exception:
        return False, "snapshot_repo unavailable"
    now = datetime.now(timezone.utc)
    for key in ("regime_current", "allocation_matrix"):
        row = get_latest_snapshot_sync(db, key)
        if not row or not row.get("generated_at"):
            return False, f"{key} missing or no generated_at"
        try:
            gen = row["generated_at"]
            if hasattr(gen, "timestamp"):
                ts = gen.timestamp()
            else:
                s = str(gen).replace("Z", "+00:00")
                ts = datetime.fromisoformat(s).timestamp()
            age = now.timestamp() - ts
            if age > MAX_STALE_SEC:
                return False, f"{key} stale {int(age)}s > {MAX_STALE_SEC}"
        except Exception as e:
            return False, f"{key} parse error: {e}"
    return True, "freshness OK"
