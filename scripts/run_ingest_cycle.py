# scripts/run_ingest_cycle.py — 통신점검 완료 뉴스/공시/자료원 전부 수집 → ext_event_raw (event_repo 경유)

from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
os.chdir(_ROOT)
from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

from backend.app.workers.ingest_worker import run_ingest_cycle_sync


def main() -> int:
    n = run_ingest_cycle_sync()
    print(f"[OK] ingest cycle done, inserted={n} rows into ext_event_raw")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
