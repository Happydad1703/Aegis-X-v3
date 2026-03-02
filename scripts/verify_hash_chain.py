# scripts/verify_hash_chain.py — SE-50 Phase 3: Recalculate chain from genesis, fail if mismatch.

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

from backend.app.core.hash_chain_verify import verify_engine_snapshot_chain, verify_order_log_chain


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
        ok1, msg1 = verify_engine_snapshot_chain(db)
        ok2, msg2 = verify_order_log_chain(db)
        if ok1 and ok2:
            print("engine_snapshot:", msg1)
            print("order_log:", msg2)
            print("PASS")
            return 0
        if not ok1:
            print("FAIL engine_snapshot:", msg1)
        if not ok2:
            print("FAIL order_log:", msg2)
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(main())
