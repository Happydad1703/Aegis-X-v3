# scripts/run_engine_comm_check.py — 뉴스 소화 엔진 연동 통신점검
# 1) 외부 자료원 API 점검  2) 수집→DB 기록  3) 엔진 1회 실행  4) 스냅샷(regime/allocation 등) 존재 확인

from __future__ import annotations

import subprocess
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


def run(cmd: list[str], desc: str) -> bool:
    """Run command; return True if exit code 0."""
    try:
        r = subprocess.run(cmd, cwd=ROOT, timeout=120, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[FAIL] {desc}: exit {r.returncode}")
            if r.stderr:
                print(r.stderr[:500])
            return False
        print(f"[OK] {desc}")
        return True
    except Exception as e:
        print(f"[FAIL] {desc}: {e}")
        return False


def main() -> int:
    print("=" * 60)
    print("AEGIS-X v3 — 뉴스 소화 엔진 통신점검")
    print("=" * 60)

    # 1) 외부 자료원 API 통신점검
    print("\n[1/4] 외부 자료원 API 통신점검 (check_comm.py)")
    ok_comm = run([sys.executable, "scripts/check_comm.py"], "외부 API 통신점검")
    if not ok_comm:
        print("  → 일부 API FAIL/SKIP. 환경변수 확인 후 재실행.")

    # 2) 수집 1회 실행 (ext_event_raw 기록)
    print("\n[2/4] 수집 1회 실행 (ingest → ext_event_raw)")
    ok_ingest = run([sys.executable, "scripts/run_ingest_cycle.py"], "Ingest cycle")
    if not ok_ingest:
        print("  → DB 미연결 또는 ext_event_raw 없음. 마이그레이션: .\\scripts\\migrate_db.ps1")

    # 3) 엔진 1회 실행 (regime → allocation → fleet_budget → core)
    print("\n[3/4] 엔진 1회 실행 (regime / allocation / fleet_budget / core)")
    ok_engine = run([sys.executable, "scripts/run_engine_cycle.py"], "Engine cycle")
    if not ok_engine:
        print("  → DB 또는 engine_snapshot 테이블 확인.")

    # 4) 뉴스 소화 엔진 출력 스냅샷 존재 확인
    print("\n[4/4] 뉴스 소화 엔진 출력 스냅샷 확인 (engine_snapshot)")
    try:
        from sqlalchemy import text
        from backend.app.core.db import SessionLocal

        db = SessionLocal()
        try:
            rows = db.execute(
                text("""
                    SELECT snapshot_key, COUNT(*) AS cnt, MAX(generated_at) AS latest
                    FROM engine_snapshot
                    WHERE snapshot_key IN ('regime_current','allocation_matrix','fleet_budget_snapshot','core_force_state','swing_force_state','strike_force_state')
                    GROUP BY snapshot_key
                    ORDER BY snapshot_key
                """)
            ).mappings().fetchall()
        except Exception as e:
            err = str(e).lower()
            if "engine_snapshot" in err or "does not exist" in err or "undefinedtable" in err:
                print("[SKIP] engine_snapshot 테이블 없음. 마이그레이션 후 3단계 재실행.")
            else:
                print(f"[FAIL] {e}")
            rows = []
        finally:
            db.close()

        if rows:
            print(f"  {'snapshot_key':<25} {'cnt':>6}  latest")
            print("  " + "-" * 50)
            for r in rows:
                latest = r.get("latest")
                if hasattr(latest, "isoformat"):
                    latest = latest.isoformat()[:22]
                print(f"  {(r.get('snapshot_key') or ''):<25} {r.get('cnt') or 0:>6}  {latest}")
            print("  [OK] 뉴스 소화 엔진 출력이 engine_snapshot에 기록됨.")
        else:
            print("  [SKIP] regime_current 등 없음. 3단계(엔진 1회 실행) 선행 필요.")
    except Exception as e:
        print(f"  [FAIL] {e}")

    print("\n" + "=" * 60)
    if ok_comm:
        print("통신점검 요약: 외부 API 점검 통과. (수집/엔진/DB는 환경에 따라 SKIP 가능)")
    else:
        print("통신점검 요약: 외부 API 일부 실패. docs/COMM_STATUS_REPORT.md 참고.")
    print("=" * 60)
    return 0 if ok_comm else 1


if __name__ == "__main__":
    sys.exit(main())
