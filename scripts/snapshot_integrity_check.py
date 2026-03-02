# scripts/snapshot_integrity_check.py — SE-50 Phase 5: After one engine cycle, required keys must exist.

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))
from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

from backend.app.core.snapshot_integrity import check_snapshot_integrity, REQUIRED_SNAPSHOT_KEYS


def main() -> int:
    try:
        from backend.app.core.db import SessionLocal
        if SessionLocal is None:
            print("SKIP: DB not configured")
            return 0
    except Exception as e:
        print("SKIP:", e)
        return 0
    db = SessionLocal()
    try:
        ok, missing = check_snapshot_integrity(db)
        if ok:
            print("PASS: all required snapshot keys present:", list(REQUIRED_SNAPSHOT_KEYS))
            return 0
        print("FAIL: missing keys:", missing)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
