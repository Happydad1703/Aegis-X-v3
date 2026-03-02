# scripts/debug_db_target.py — Phase 0-1: Verify DB target in <20 seconds.
# Prints: current_database(), current_user, inet_server_addr(), inet_server_port(), to_regclass('public.engine_snapshot').
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    load_dotenv(_ROOT / ".env")
    url = os.getenv("DATABASE_URL", "").strip()

    if not url:
        print("[FAIL] DATABASE_URL is empty. Check .env and Windows env vars.")
        return 2

    # Mask password in log
    _masked = url
    if "@" in url and "://" in url:
        try:
            pre, rest = url.split("@", 1)
            if ":" in pre:
                scheme, rest2 = pre.split("://", 1)
                if ":" in rest2:
                    user, _ = rest2.split(":", 1)
                    _masked = f"{scheme}://{user}:****@{rest}"
        except Exception:
            pass
    print("[INFO] DATABASE_URL =", _masked)

    try:
        engine = create_engine(url, pool_pre_ping=True)
    except Exception as e:
        print("[FAIL] create_engine() failed:", repr(e))
        return 3

    with engine.connect() as c:
        row = c.execute(
            text("SELECT current_database() AS db, current_user AS usr, inet_server_addr() AS addr, inet_server_port() AS port")
        ).mappings().first()
        reg = c.execute(text("SELECT to_regclass('public.engine_snapshot') AS reg")).mappings().first()

    print("current_database() =", row["db"])
    print("current_user       =", row["usr"])
    print("inet_server_addr() =", row["addr"])
    print("inet_server_port() =", row["port"])
    print("to_regclass('public.engine_snapshot') =", reg["reg"])
    if reg is None or reg["reg"] is None:
        print("[FAIL] engine_snapshot table not found. DATABASE_URL이 가리키는 DB에 마이그레이션이 적용되지 않았습니다.")
        print("[RECOVERY] 1) DATABASE_URL과 동일한 DB에 스키마 적용:")
        print("            python scripts\\migrate_db_via_url.py")
        print("[RECOVERY] 2) 포트 확인: netstat -ano | findstr 5433  /  docker port aegisx-db")
        print("[RECOVERY] 3) docs/Stability_Check_Report_Unresolvable.md §3.2 참조")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
