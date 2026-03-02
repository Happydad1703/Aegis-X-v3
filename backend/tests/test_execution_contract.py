# backend/tests/test_execution_contract.py — Engines never call KIS; no direct broker/network in engines.
# Verification_Playbook: pytest backend/tests/test_execution_contract.py

from __future__ import annotations

import importlib.util
import os


def test_engines_no_kis_import() -> None:
    """Engine modules must not import kis_executor or any KIS broker client (P5: execution separation)."""
    engine_names = ["regime_engine", "allocation_engine", "fleet_budget_engine", "core_engine", "swing_engine", "strike_engine"]
    backend_root = os.path.join(os.path.dirname(__file__), "..", "app", "engines")
    for name in engine_names:
        path = os.path.join(backend_root, f"{name}.py")
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "kis_executor" not in content, f"{name} must not reference kis_executor"
        for line in content.splitlines():
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if "import" in stripped and "kis" in stripped.lower():
                raise AssertionError(f"{name} must not import KIS: {line.strip()}")
            if stripped.startswith("from ") and "kis" in stripped.lower():
                raise AssertionError(f"{name} must not import from KIS module: {line.strip()}")


def test_engines_no_sqlalchemy_import() -> None:
    """Engine modules must not import sqlalchemy (P2 purity: no DB)."""
    engine_names = ["regime_engine", "allocation_engine", "fleet_budget_engine", "core_engine", "swing_engine", "strike_engine"]
    backend_root = os.path.join(os.path.dirname(__file__), "..", "app", "engines")
    for name in engine_names:
        path = os.path.join(backend_root, f"{name}.py")
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "sqlalchemy" not in content.lower(), f"{name} must not import sqlalchemy (engine purity P2)"


def test_engines_no_requests_httpx_in_engines() -> None:
    """Engine modules must not import requests or httpx (no network in engines)."""
    engine_names = ["regime_engine", "allocation_engine", "fleet_budget_engine", "core_engine", "swing_engine", "strike_engine"]
    backend_root = os.path.join(os.path.dirname(__file__), "..", "app", "engines")
    for name in engine_names:
        path = os.path.join(backend_root, f"{name}.py")
        if not os.path.isfile(path):
            continue
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "import requests" not in content and "from requests" not in content, (
            f"{name} must not import requests"
        )
        assert "import httpx" not in content and "from httpx" not in content, (
            f"{name} must not import httpx"
        )
