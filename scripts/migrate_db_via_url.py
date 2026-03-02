# scripts/migrate_db_via_url.py — Apply migrations using DATABASE_URL (same DB as Python/app).
# Use this when Python and Docker might target different DBs; ensures the DB your app uses gets the schema.
# Migrations: db/migrations/001_init_core.sql .. 004_fleet.sql (same order as migrate_db.ps1).

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

# psycopg2 URL: SQLAlchemy uses postgresql+psycopg2; we need raw psycopg2 for execute
def _get_psycopg2_url() -> str:
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        print("[FAIL] DATABASE_URL is empty. Set .env or environment.")
        sys.exit(2)
    if url.startswith("postgresql://"):
        return url
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql://", 1)
    return url


def main() -> int:
    url = _get_psycopg2_url()
    print("[INFO] Applying migrations via DATABASE_URL (same DB as app)...")

    from sqlalchemy import create_engine, text

    engine = create_engine(url, pool_pre_ping=True)
    migrations_dir = _ROOT / "db" / "migrations"
    if not migrations_dir.is_dir():
        print("[FAIL] db/migrations not found.")
        return 3

    # Use raw connection so SQL colons (e.g. in JSON) are not interpreted as bind parameters
    files = ["001_init_core.sql", "002_order_log.sql", "003_hash_chain_columns.sql", "004_fleet.sql"]
    for name in files:
        path = migrations_dir / name
        if not path.is_file():
            continue
        sql = path.read_text(encoding="utf-8", errors="replace")
        if not sql.strip():
            continue
        try:
            with engine.raw_connection() as raw_conn:
                dbapi = getattr(raw_conn, "driver_connection", getattr(raw_conn, "connection", raw_conn))
                cur = dbapi.cursor()
                try:
                    cur.execute(sql)
                    dbapi.commit()
                finally:
                    cur.close()
        except Exception as e:
            print(f"[FAIL] Migration {name}: {e}")
            return 4
        print(f"[OK] {name}")

    print("Migration complete (via URL).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
