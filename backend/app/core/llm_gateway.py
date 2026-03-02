# core/llm_gateway.py — SE-58, LLM_Fallback_Plan: Multi-provider fallback. 통신 두절 ≠ 실행 안정성 하락.

from __future__ import annotations

import time
from typing import Any, Optional

# Role constants (SE-58)
ROLE_JCS = "JCS"
ROLE_STRATCOM = "STRATCOM"
ROLE_SRC = "SRC"
ROLE_STRIKE = "Strike"
ROLE_RESERVE = "Reserve"

# Fallback chain order (LLM_Fallback_Plan). 활용 가능한 모든 LLM 순차 시도.
FALLBACK_PROVIDER_ORDER = ("openai", "anthropic", "gemini", "deepseek")


def _try_openai(prompt: str, max_tokens: int = 500) -> tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """Returns (ok, model_used, text, error)."""
    try:
        from backend.app.core.env_keys import get_llm_openai_key
        key = get_llm_openai_key()
        if not key:
            return False, None, None, "OPENAI_API_KEY not set"
        import requests
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "gpt-4o-mini", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens},
            timeout=30,
        )
        if r.status_code != 200:
            return False, None, None, f"HTTP {r.status_code}"
        data = r.json()
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
        model = data.get("model", "gpt-4o-mini")
        return bool(text), model, text or None, None
    except Exception as e:
        return False, None, None, str(e)


def _try_anthropic(prompt: str, max_tokens: int = 500) -> tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """Returns (ok, model_used, text, error)."""
    try:
        from backend.app.core.env_keys import get_llm_claude_key
        key = get_llm_claude_key()
        if not key:
            return False, None, None, "ANTHROPIC_API_KEY not set"
        import requests
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={"model": "claude-3-haiku-20240307", "max_tokens": max_tokens, "messages": [{"role": "user", "content": prompt}]},
            timeout=30,
        )
        if r.status_code != 200:
            return False, None, None, f"HTTP {r.status_code}"
        data = r.json()
        text = (data.get("content") or [{}])[0].get("text", "").strip()
        model = data.get("model", "claude-3-haiku")
        return bool(text), model, text or None, None
    except Exception as e:
        return False, None, None, str(e)


def _try_gemini(prompt: str, max_tokens: int = 500) -> tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """Returns (ok, model_used, text, error)."""
    try:
        from backend.app.core.env_keys import get_llm_gemini_key
        key = get_llm_gemini_key()
        if not key:
            return False, None, None, "GEMINI/GOOGLE_API_KEY not set"
        import requests
        for model in ("gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"):
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"maxOutputTokens": max_tokens}},
                timeout=30,
            )
            if r.status_code in (200, 201):
                data = r.json()
                text = "".join(
                    p.get("text", "") for c in (data.get("candidates") or [])
                    for p in (c.get("content", {}).get("parts") or [])
                ).strip()
                if text:
                    return True, model, text, None
        return False, None, None, "no model available"
    except Exception as e:
        return False, None, None, str(e)


def _try_deepseek(prompt: str, max_tokens: int = 500) -> tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """Returns (ok, model_used, text, error)."""
    try:
        from backend.app.core.env_keys import get_llm_deepseek_key
        key = get_llm_deepseek_key()
        if not key:
            return False, None, None, "DEEPSEEK_API_KEY not set"
        import requests
        r = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "max_tokens": max_tokens},
            timeout=30,
        )
        if r.status_code != 200:
            return False, None, None, f"HTTP {r.status_code}"
        data = r.json()
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
        model = data.get("model", "deepseek-chat")
        return bool(text), model, text or None, None
    except Exception as e:
        return False, None, None, str(e)


_PROVIDER_FUNCS = {
    "openai": _try_openai,
    "anthropic": _try_anthropic,
    "gemini": _try_gemini,
    "deepseek": _try_deepseek,
}


def request_llm(
    role: str,
    task_type: str,
    payload: dict,
    *,
    providers: list[str] | None = None,
    max_latency_ms: int = 30_000,
    db: Any = None,
) -> dict[str, Any]:
    """
    Multi-provider fallback: 1선(OpenAI) → 2선(Anthropic) → 3선(Gemini) → 4선(DeepSeek).
    전원 실패 시: on_blackout(db) 호출 후 LKS 반환. 특정 LLM 통신 두절이 시스템 실행 안정성 하락으로 이어지지 않음.
    Returns: {ok, provider_used, model_used, latency_ms, result, error, lks_fallback}.
    """
    prompt = payload.get("prompt", "") or str(payload)[:4000]
    max_tokens = min(2000, payload.get("max_tokens", 500))
    order = providers or list(FALLBACK_PROVIDER_ORDER)
    t0 = time.perf_counter()

    for name in order:
        fn = _PROVIDER_FUNCS.get(name)
        if not fn:
            continue
        ok, model_used, text, err = fn(prompt, max_tokens)
        latency_ms = int((time.perf_counter() - t0) * 1000)
        if ok and text:
            if db is not None:
                try:
                    from backend.app.core.config_service import set_config
                    set_config(db, "llm_blackout_active", {"active": False}, "llm_gateway")
                except Exception:
                    pass
            return {
                "ok": True,
                "provider_used": name,
                "model_used": model_used,
                "latency_ms": latency_ms,
                "result": {"text": text},
                "error": None,
                "lks_fallback": False,
            }
        if latency_ms >= max_latency_ms:
            break

    # Blackout: all failed — record incident and return LKS so system continues
    lks = {}
    if db is not None:
        try:
            on_blackout(db)
            lks = get_lks(db)
        except Exception:
            pass
    return {
        "ok": False,
        "provider_used": None,
        "model_used": None,
        "latency_ms": int((time.perf_counter() - t0) * 1000),
        "result": lks if lks else {"message": "LKS empty; structured-only mode."},
        "error": "LLM_BLACKOUT",
        "lks_fallback": True,
    }


def get_health() -> dict[str, Any]:
    """Skeleton: Provider-wise health (latency, error_rate, last_ok_at)."""
    return {"providers": {}, "status": "unknown"}


def get_lks(db) -> dict[str, Any]:
    """Last-Known Strategy: load from DB (system_config)."""
    from backend.app.core import config_service
    out = config_service.get_config(db, "lks_last_known_strategy")
    return out if isinstance(out, dict) else {}


def record_lks(db, lks: dict[str, Any]) -> None:
    """Persist LKS to DB for blackout recovery."""
    from backend.app.core import config_service
    config_service.set_config(db, "lks_last_known_strategy", lks, "llm_gateway")


def on_blackout(db) -> None:
    """On full LLM failure: record incident_log + set Execution Freeze (block_new_orders, allow_only_risk_reduction)."""
    from backend.app.core.incident_repo import create_incident
    from backend.app.core.config_service import set_config
    create_incident(db, "WARNING", "LLM_BLACKOUT", "All LLM providers failed; LKS mode.", "llm_status")
    set_config(db, "llm_blackout_active", {"active": True, "block_new_orders": True, "allow_only_risk_reduction": True}, "llm_gateway")
