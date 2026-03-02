# scripts/verify_ingest_db.py — 통신점검 완료 뉴스/공시/자료원 → ext_event_raw 기록 여부 확인
# 사용: python scripts/verify_ingest_db.py [--run-ingest]

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    pass


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify ext_event_raw has data from all ingest sources.")
    parser.add_argument("--run-ingest", action="store_true", help="Run one ingest cycle before verifying.")
    args = parser.parse_args()

    if args.run_ingest:
        from backend.app.workers.ingest_worker import run_ingest_cycle_sync
        n = run_ingest_cycle_sync()
        print(f"[OK] Ingest cycle done, inserted={n} rows")

    from sqlalchemy import text
    from backend.app.core.db import SessionLocal

    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT source_name, event_type, COUNT(*) AS cnt, MAX(received_at) AS latest
                FROM ext_event_raw
                GROUP BY source_name, event_type
                ORDER BY source_name, event_type
            """)
        ).mappings().fetchall()
    except Exception as e:
        err = str(e).lower()
        if "ext_event_raw" in err or "undefinedtable" in err or "does not exist" in err:
            print("[FAIL] ext_event_raw 테이블이 없습니다. 먼저 마이그레이션 실행: .\\scripts\\migrate_db.ps1")
        else:
            print(f"[FAIL] DB query error: {e}")
        return 1
    finally:
        db.close()

    if not rows:
        print("[FAIL] ext_event_raw has no rows. Run: python scripts/run_ingest_cycle.py")
        return 1

    print("\n--- ext_event_raw 기록 현황 (source_name, event_type, 건수, 최신 수신 시각) ---")
    print(f"{'source_name':<20} {'event_type':<15} {'cnt':>6}  latest")
    print("-" * 70)
    for r in rows:
        src = (r["source_name"] or "")[:19]
        typ = (r["event_type"] or "")[:14]
        cnt = r["cnt"] or 0
        latest = r["latest"]
        if hasattr(latest, "isoformat"):
            latest = latest.isoformat()[:22]
        print(f"{src:<20} {typ:<15} {cnt:>6}  {latest}")
    print("-" * 70)
    print(f"Total source/type combinations: {len(rows)}")
    print("\n[OK] 자료가 ext_event_raw에 기록되고 있음. (event_repo 단일 기록 경로)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
