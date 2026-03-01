# scripts/debug_db_target.py
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

    print("[INFO] DATABASE_URL =", url)

    try:
        engine = create_engine(url, pool_pre_ping=True)
    except Exception as e:
        print("[FAIL] create_engine() failed:", repr(e))
        return 3

    with engine.connect() as c:
        whoami = c.execute(
            text("select current_database(), current_user, inet_server_addr(), inet_server_port()")
        ).fetchone()
        reg = c.execute(text("select to_regclass('public.engine_snapshot')")).fetchone()

    print("[OK] current_database/current_user/server_addr/server_port =", whoami)
    print("[OK] to_regclass(public.engine_snapshot) =", reg[0])
    if reg is None or reg[0] is None:
        print("[FAIL] engine_snapshot table not found. Run migrate_db.ps1 and ensure DATABASE_URL points to that DB.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
