# scripts/run_ingest_cycle.py — Phase 1-1: one ingest cycle (heartbeat + optional FRED) → ext_event_raw

from __future__ import annotations

from backend.app.workers.ingest_worker import run_ingest_cycle_sync


def main() -> int:
    n = run_ingest_cycle_sync()
    print(f"[OK] ingest cycle done, inserted={n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
