"""
Aegis-X v3 내부 시뮬레이션
SE 문서(64, 65, 43, 14_TVP) 기준으로 시스템 개발 가능성 구도를 검증한다.
실행: python scripts/internal_simulation.py
"""
from __future__ import annotations

import os
import re
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
BACKEND_APP = ROOT / "backend" / "app"
DOCS = ROOT / "docs"
DB_MIGRATIONS = ROOT / "db" / "migrations"

# 65 명세: backend/app 하위 필수 디렉터리·파일
STRUCTURE_65 = {
    "core": ["db.py", "snapshot_repo.py", "incident_repo.py", "command_repo.py", "mode_service.py", "config_service.py", "resource_monitor.py"],
    "engines": ["regime_engine.py", "allocation_engine.py", "fleet_budget_engine.py", "capital_scaling.py", "health_engine.py", "strike_engine.py", "swing_engine.py", "core_engine.py"],
    "gates": ["pre_trade_gate.py", "cap_gate.py", "risk_gate.py", "freshness_gate.py", "mode_gate.py", "crisis_gate.py"],
    "execution": ["paper_executor.py", "kis_executor.py"],
    "workers": ["engine_worker.py", "ingest_worker.py"],
    "api": ["control.py", "cic.py", "health.py", "pilot.py"],
    "models": ["schemas.py"],
    "utils": ["time_utils.py"],
}

# 64/43 필수 테이블
REQUIRED_TABLES = [
    "ext_event_raw",
    "engine_snapshot",
    "system_mode",
    "system_config",
    "incident_log",
    "command_log",
]
OPTIONAL_TABLES_64 = ["macro_context", "engine_result", "order_log", "battle_report"]

# Phase 0-1 정본 Snapshot 6종
SNAPSHOT_KEYS_64 = [
    "engine_heartbeat",
    "comm_health",
    "regime_current",
    "operation_mode",
    "llm_status",
    "risk_guard",
]


def run_structure_simulation() -> tuple[list[str], list[str]]:
    """65 디렉터리 구조 준수 여부."""
    ok, fail = [], []
    for folder, files in STRUCTURE_65.items():
        dir_path = BACKEND_APP / folder
        if not dir_path.is_dir():
            fail.append(f"Missing directory: backend/app/{folder}")
            continue
        for f in files:
            if (dir_path / f).is_file():
                ok.append(f"backend/app/{folder}/{f}")
            else:
                fail.append(f"Missing: backend/app/{folder}/{f}")
    return ok, fail


def run_ddl_simulation() -> tuple[list[str], list[str]]:
    """001_init_core.sql이 64/43 필수 테이블 포함 여부."""
    ok, fail = [], []
    sql_path = DB_MIGRATIONS / "001_init_core.sql"
    if not sql_path.is_file():
        fail.append("db/migrations/001_init_core.sql not found")
        return ok, fail
    text = sql_path.read_text(encoding="utf-8")
    for table in REQUIRED_TABLES:
        if re.search(rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{re.escape(table)}\s*\(", text, re.I):
            ok.append(f"Table: {table}")
        else:
            fail.append(f"Missing table in DDL: {table}")
    for table in OPTIONAL_TABLES_64:
        if re.search(rf"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?{re.escape(table)}\s*\(", text, re.I):
            ok.append(f"Table (64 optional): {table}")
    if "TIMESTAMPTZ" in text.upper() or "NOW()" in text:
        ok.append("TIMESTAMPTZ/NOW() used")
    if "JSONB" in text.upper():
        ok.append("JSONB used for JSON columns")
    return ok, fail


def run_snapshot_simulation() -> tuple[list[str], list[str]]:
    """engine_worker가 Snapshot 6종 산출 경로 보유 여부 (코드 기준)."""
    ok, fail = [], []
    worker_path = BACKEND_APP / "workers" / "engine_worker.py"
    if not worker_path.is_file():
        fail.append("workers/engine_worker.py not found")
        return ok, fail
    text = worker_path.read_text(encoding="utf-8")
    for key in SNAPSHOT_KEYS_64:
        if f'snapshot_key="{key}"' in text or f"snapshot_key='{key}'" in text or f'"{key}"' in text:
            ok.append(f"Snapshot key produced: {key}")
        else:
            fail.append(f"Snapshot key not produced in engine_worker: {key}")
    if "insert_snapshot" in text:
        ok.append("insert_snapshot (snapshot_repo) used")
    return ok, fail


def run_boundary_simulation() -> tuple[list[str], list[str]]:
    """engines에 DB/SQL 직접 사용 없음, snapshot 단일 경로."""
    ok, fail = [], []
    engines_dir = BACKEND_APP / "engines"
    if not engines_dir.is_dir():
        fail.append("engines/ not found")
        return ok, fail
    for py in engines_dir.glob("*.py"):
        content = py.read_text(encoding="utf-8")
        if "sqlalchemy" in content.lower() or "text(" in content or "execute(" in content or "Session" in content:
            fail.append(f"engines/{py.name}: DB/SQL usage detected (violates 65)")
        else:
            ok.append(f"engines/{py.name}: no direct DB")
    if (BACKEND_APP / "core" / "snapshot_repo.py").is_file():
        ok.append("core/snapshot_repo.py exists (single write path)")
    return ok, fail


def main() -> None:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    report_lines = [
        "# Aegis-X v3 Internal Simulation Report",
        "",
        f"**Generated**: {ts} (UTC)",
        "",
        "기준: docs/64_Phase0_1, 65_Final_Directory_Architecture_Lock, 43_DB_Schema, 14_TVP",
        "",
        "---",
        "",
    ]
    all_ok = 0
    all_fail = 0

    # 1) 구조
    o1, f1 = run_structure_simulation()
    report_lines.append("## 1. Structure (65)\n")
    if f1:
        report_lines.append("**FAIL**\n")
        for x in f1:
            report_lines.append(f"- ❌ {x}")
        all_fail += len(f1)
    else:
        report_lines.append("**PASS**\n")
    for x in o1:
        report_lines.append(f"- ✅ {x}")
        all_ok += 1
    report_lines.append("")

    # 2) DDL
    o2, f2 = run_ddl_simulation()
    report_lines.append("## 2. DDL (64/43)\n")
    if f2:
        report_lines.append("**FAIL**\n")
        for x in f2:
            report_lines.append(f"- ❌ {x}")
        all_fail += len(f2)
    else:
        report_lines.append("**PASS**\n")
    for x in o2:
        report_lines.append(f"- ✅ {x}")
        all_ok += 1
    report_lines.append("")

    # 3) Snapshot 6종
    o3, f3 = run_snapshot_simulation()
    report_lines.append("## 3. Snapshot 6 Keys (64)\n")
    if f3:
        report_lines.append("**GAP (미구현)**\n")
        for x in f3:
            report_lines.append(f"- ⚠️ {x}")
        all_fail += len(f3)
    else:
        report_lines.append("**PASS**\n")
    for x in o3:
        report_lines.append(f"- ✅ {x}")
        all_ok += 1
    report_lines.append("")

    # 4) 경계
    o4, f4 = run_boundary_simulation()
    report_lines.append("## 4. Module Boundary (65)\n")
    if f4:
        report_lines.append("**FAIL**\n")
        for x in f4:
            report_lines.append(f"- ❌ {x}")
        all_fail += len(f4)
    else:
        report_lines.append("**PASS**\n")
    for x in o4:
        report_lines.append(f"- ✅ {x}")
        all_ok += 1
    report_lines.append("")

    # Summary
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("## Summary")
    report_lines.append("")
    report_lines.append(f"- Pass: {all_ok}")
    report_lines.append(f"- Fail/Gap: {all_fail}")
    if all_fail == 0:
        report_lines.append("")
        report_lines.append("**Result: GO** — 시스템 개발 구도 기준 충족. Phase 0-1 개발 착수 가능.")
    else:
        report_lines.append("")
        report_lines.append("**Result: GO with GAPs** — 갭 보완 후 재시뮬레이션 권장. (구조/DDL 통과 시 개발 착수 가능, Snapshot 6종·경계는 단계적 보완)")

    report_text = "\n".join(report_lines)
    report_path = DOCS / "Internal_Simulation_Report.md"
    report_path.write_text(report_text, encoding="utf-8")

    # Console
    print("=" * 60)
    print("Aegis-X v3 Internal Simulation")
    print("=" * 60)
    print(f"1. Structure (65)  : {'PASS' if not f1 else 'FAIL'} ({len(o1)} ok, {len(f1)} fail)")
    print(f"2. DDL (64/43)     : {'PASS' if not f2 else 'FAIL'} ({len(o2)} ok, {len(f2)} fail)")
    print(f"3. Snapshot 6 Keys : {'PASS' if not f3 else 'GAP'}  ({len(o3)} ok, {len(f3)} gap)")
    print(f"4. Boundary (65)   : {'PASS' if not f4 else 'FAIL'} ({len(o4)} ok, {len(f4)} fail)")
    print("=" * 60)
    print(f"Total: {all_ok} pass, {all_fail} fail/gap")
    print(f"Report: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
