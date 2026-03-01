# backend/tests/test_contract_ui_never_calls_compute.py
# SOP / Hard Lock: UI/API MUST NOT import compute (engines). DB-Only Read.

from __future__ import annotations

import ast
import os
import pytest

# Paths that must NOT import from backend.app.engines (or engines.*)
FORBIDDEN_UI_IMPORT_PATHS = [
    "backend/app/api",
    "backend/main.py",
]


def _collect_py_files_under(root: str, base_dir: str) -> list[str]:
    out = []
    if os.path.isfile(root):
        if root.endswith(".py"):
            out.append(root)
        return out
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.isdir(path) and name in ("__pycache__", ".pytest_cache", "tests"):
            continue
        if os.path.isdir(path):
            out.extend(_collect_py_files_under(path, base_dir))
        elif name.endswith(".py"):
            out.append(path)
    return out


def _has_engines_import(filepath: str) -> bool:
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "backend.app.engines" or alias.name.startswith("backend.app.engines."):
                    return True
        if isinstance(node, ast.ImportFrom):
            if node.module and (
                node.module == "backend.app.engines" or node.module.startswith("backend.app.engines.")
            ):
                return True
    return False


@pytest.fixture(scope="session")
def project_root():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_ui_never_calls_compute(project_root: str) -> None:
    """UI/API layer must NOT import from engines/. Contract: DB-Only Read."""
    violations = []
    for item in FORBIDDEN_UI_IMPORT_PATHS:
        full = os.path.join(project_root, item.replace("/", os.sep))
        if os.path.isfile(full):
            files = [full]
        else:
            files = _collect_py_files_under(full, project_root)
        for path in files:
            if _has_engines_import(path):
                rel = os.path.relpath(path, project_root)
                violations.append(rel)
    assert not violations, (
        "UI/API must not import engines (DB-Only Read). Violations: " + ", ".join(violations)
    )
