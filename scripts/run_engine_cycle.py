# scripts/run_engine_cycle.py
from __future__ import annotations

import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
os.chdir(_ROOT)
# 프로젝트 루트 .env 강제 로드 (DB URL 일치 보장)
from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

from backend.app.core.db import SessionLocal
from backend.app.workers.engine_worker import run_single_cycle_sync


def main() -> int:
    db = SessionLocal()
    try:
        run_single_cycle_sync(db)
    finally:
        db.close()
    print("[OK] engine cycle done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
