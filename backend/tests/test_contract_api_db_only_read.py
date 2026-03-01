# backend/tests/test_contract_api_db_only_read.py
# Guardrail A: API/UI must ONLY read from engine_snapshot for UI logic.
# Direct reads from ext_event_raw, order_log (주문/포지션) in API layer are forbidden.

from __future__ import annotations

import os
import pytest

# Paths that must NOT contain direct query to forbidden tables
API_PATHS = [
    "backend/app/api",
    "backend/main.py",
]

# Forbidden table names in API layer (DB-Only Read: UI reads engine_snapshot only)
FORBIDDEN_TABLE_NAMES = (
    "ext_event_raw",
    "order_log",
)


def _collect_py_files(root: str) -> list[str]:
    out = []
    if os.path.isfile(root):
        return [root] if root.endswith(".py") else []
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isdir(path) and name in ("__pycache__", ".pytest_cache"):
            continue
        if os.path.isdir(path):
            out.extend(_collect_py_files(path))
        elif name.endswith(".py"):
            out.append(path)
    return out


@pytest.fixture(scope="session")
def project_root():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_api_only_reads_engine_snapshot_no_forbidden_tables(project_root: str) -> None:
    """API must not directly query ext_event_raw, order_log. DB-Only Read: engine_snapshot only for UI."""
    violations = []
    for item in API_PATHS:
        full = os.path.join(project_root, item.replace("/", os.sep))
        if os.path.isfile(full):
            files = [full]
        else:
            files = _collect_py_files(full) if os.path.isdir(full) else []
        for path in files:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            for table in FORBIDDEN_TABLE_NAMES:
                if table in content:
                    rel = os.path.relpath(path, project_root)
                    violations.append(f"{rel}: references forbidden table '{table}'")
    assert not violations, (
        "DB-Only Read: API must not query ext_event_raw or order_log. "
        "Use engine_snapshot only. Violations: " + "; ".join(violations)
    )
