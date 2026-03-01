# workers/ingest_worker.py — SE-03 ICD, 04 DDD: 외부 소스 → ext_event_raw (event_repo 경유)
# Phase 1-1: 최소 1개 소스 → ext_event_raw 행 증가. Workers may do I/O; DB write via core/event_repo only.

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.core.db import SessionLocal
from backend.app.core.env_keys import get_fred_api_key
from backend.app.core.event_repo import insert_raw_event_sync


def _ingest_heartbeat_sync() -> int:
    """Minimal source: heartbeat event. Ensures ext_event_raw has rows (no API key required)."""
    db = SessionLocal()
    try:
        insert_raw_event_sync(
            db,
            source_name="ingest_worker",
            event_type="heartbeat",
            payload={"ts_utc": datetime.now(timezone.utc).isoformat(), "source": "heartbeat"},
        )
        return 1
    finally:
        db.close()


def _ingest_fred_one_series_sync() -> int:
    """Optional: one FRED series if FRED_API_KEY set. Otherwise skips."""
    key = get_fred_api_key()
    if not key:
        return 0
    try:
        import urllib.request
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DFEDTARU&api_key={key}&file_type=json"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = r.read().decode()
        import json as _json
        obj = _json.loads(data)
        obs = obj.get("observations", [])[:1]
        if not obs:
            return 0
        db = SessionLocal()
        try:
            insert_raw_event_sync(
                db,
                source_name="FRED",
                event_type="macro",
                payload={"series": "DFEDTARU", "observations": obs, "ts_utc": datetime.now(timezone.utc).isoformat()},
            )
            return 1
        finally:
            db.close()
    except Exception:
        return 0


def run_ingest_cycle_sync() -> int:
    """Run one ingest cycle: heartbeat + optional FRED. Returns total rows inserted this cycle."""
    n = _ingest_heartbeat_sync()
    n += _ingest_fred_one_series_sync()
    return n
