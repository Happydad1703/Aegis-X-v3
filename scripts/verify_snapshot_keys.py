# scripts/verify_snapshot_keys.py — Phase 0-1: after one engine cycle, required snapshot keys must exist.
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from backend.app.core.snapshot_keys import REQUIRED_SNAPSHOT_KEYS_MINIMUM
REQUIRED = list(REQUIRED_SNAPSHOT_KEYS_MINIMUM)


def main() -> int:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        print("[FAIL] DATABASE_URL empty")
        return 1
    from sqlalchemy import create_engine, text
    engine = create_engine(url, pool_pre_ping=True)
    try:
        with engine.connect() as c:
            r = c.execute(text("SELECT snapshot_key FROM engine_snapshot GROUP BY snapshot_key")).fetchall()
    except Exception as e:
        print(f"[FAIL] Query error: {e}")
        return 1
    keys = [row[0] for row in r]
    missing = [k for k in REQUIRED if k not in keys]
    if missing:
        print("[FAIL] Missing snapshot keys:", missing)
        return 1
    print("[OK] Required snapshot keys present:", REQUIRED)
    return 0


if __name__ == "__main__":
    sys.exit(main())
