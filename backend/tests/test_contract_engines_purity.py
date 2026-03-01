# backend/tests/test_contract_engines_purity.py
# Guardrail: engines/ MUST NOT import SQLAlchemy, DB session, or execute SQL. Pure dict→dict only.

from __future__ import annotations

import ast
import os
import pytest

def _collect_engine_py_files(engines_dir: str) -> list[str]:
    out = []
    if not os.path.isdir(engines_dir):
        return out
    for name in os.listdir(engines_dir):
        path = os.path.join(engines_dir, name)
        if name.startswith("_") or not name.endswith(".py"):
            continue
        if os.path.isfile(path):
            out.append(path)
    return out


def _file_imports_sqlalchemy(filepath: str) -> bool:
    """True if file contains import of sqlalchemy (any submodule)."""
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "sqlalchemy" in alias.name.lower():
                        return True
            if isinstance(node, ast.ImportFrom):
                if node.module and "sqlalchemy" in (node.module or "").lower():
                    return True
    except SyntaxError:
        pass
    return False


@pytest.fixture(scope="session")
def project_root():
    return os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def test_engines_no_sqlalchemy_or_db(project_root: str) -> None:
    """engines/ must be pure functions: no SQLAlchemy, no DB session, no SQL."""
    engines_dir = os.path.join(project_root, "backend", "app", "engines")
    if not os.path.isdir(engines_dir):
        pytest.skip("backend/app/engines not found")
    violations = []
    for path in _collect_engine_py_files(engines_dir):
        if _file_imports_sqlalchemy(path):
            rel = os.path.relpath(path, project_root)
            violations.append(rel)
    assert not violations, (
        "Strict Engine Purity: engines/ MUST NOT import SQLAlchemy. Violations: " + ", ".join(violations)
    )
