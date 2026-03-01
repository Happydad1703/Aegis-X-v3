# backend/tests/test_contract_single_write_path.py
# SOP / Hard Lock: DB writes ONLY via snapshot_repo / designated repo modules.

from __future__ import annotations

import os
import re
import pytest

# Modules allowed to contain SQL INSERT/UPDATE (single write path)
ALLOWED_WRITE_MODULE_NAMES = {
    "snapshot_repo.py",
    "incident_repo.py",
    "command_repo.py",
    "config_service.py",
    "event_repo.py",
    "order_repo.py",
}


def _collect_py_files(root: str) -> list[str]:
    out = []
    if os.path.isfile(root):
        return [root] if root.endswith(".py") else []
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isdir(path) and name in ("__pycache__", ".pytest_cache", "tests", "migrations"):
            continue
        if os.path.isdir(path):
            out.extend(_collect_py_files(path))
        elif name.endswith(".py"):
            out.append(path)
    return out


# SQL write patterns: only these in designated repo modules
_INSERT_INTO = re.compile(r"\bINSERT\s+INTO\b", re.IGNORECASE)
_UPDATE_SET = re.compile(r"\bUPDATE\s+\w+\s+SET\b", re.IGNORECASE)


@pytest.fixture(scope="session")
def project_root():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_single_write_path_only(project_root: str) -> None:
    """No DB write (INSERT/UPDATE) outside designated repo modules."""
    app_dir = os.path.join(project_root, "backend", "app")
    if not os.path.isdir(app_dir):
        pytest.skip("backend/app not found")
    violations = []
    for path in _collect_py_files(app_dir):
        base = os.path.basename(path)
        if base in ALLOWED_WRITE_MODULE_NAMES:
            continue
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        if _INSERT_INTO.search(text) or _UPDATE_SET.search(text):
            rel = os.path.relpath(path, project_root)
            violations.append(rel)
    assert not violations, (
        "DB writes only via repo modules (snapshot_repo, incident_repo, command_repo, config_service). "
        "Violations: " + ", ".join(violations)
    )
