# core/hash_chain_verify.py — SE-50 Phase 3: Hash chain verification (worker/script level; UI never).

from __future__ import annotations

import hashlib
import json


def _sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def verify_engine_snapshot_chain(db) -> tuple[bool, str]:
    """Verify engine_snapshot prev_hash/self_hash chain. Returns (ok, message)."""
    from sqlalchemy import text
    try:
        rows = db.execute(
            text("SELECT id, snapshot_key, snapshot_data, generated_at, prev_hash, self_hash FROM engine_snapshot ORDER BY id")
        ).mappings().fetchall()
    except Exception as e:
        return False, f"query failed: {e}"
    if not rows:
        return True, "no rows"
    prev = "genesis"
    for r in rows:
        stored_prev = r.get("prev_hash") or "genesis"
        stored_self = r.get("self_hash")
        if stored_self is None:
            return True, "hash columns not present (migration 003 not applied)"
        if stored_prev != prev:
            return False, f"id={r['id']} prev_hash mismatch"
        payload = r.get("snapshot_data")
        if hasattr(payload, "copy"):
            payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        else:
            payload_str = json.dumps(payload or {}, sort_keys=True, ensure_ascii=False, default=str)
        ts = r.get("generated_at")
        ts_str = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
        computed = _sha256(f"{prev}{payload_str}{ts_str}")
        if computed != stored_self:
            return False, f"id={r['id']} self_hash mismatch"
        prev = stored_self
    return True, "OK"


def verify_order_log_chain(db) -> tuple[bool, str]:
    """Verify order_log prev_hash/self_hash chain."""
    from sqlalchemy import text
    try:
        rows = db.execute(
            text("SELECT id, execution_payload, created_at, prev_hash, self_hash FROM order_log ORDER BY id")
        ).mappings().fetchall()
    except Exception as e:
        return False, f"query failed: {e}"
    if not rows:
        return True, "no rows"
    prev = "genesis"
    for r in rows:
        stored_self = r.get("self_hash")
        if stored_self is None:
            return True, "hash columns not present"
        payload = r.get("execution_payload") or {}
        payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        ts = r.get("created_at")
        ts_str = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
        computed = _sha256(f"{prev}{payload_str}{ts_str}")
        if computed != stored_self:
            return False, f"id={r['id']} self_hash mismatch"
        prev = stored_self
    return True, "OK"
