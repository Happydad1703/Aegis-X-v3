# scripts/check_comm.py — SE-05, 14_TVP: 외부 기관(뉴스/정보원, LLM, KIS) API 키·통신 확인
# 모든 API Key는 Windows 11 환경변수에서 획득. 환경변수에서 읽어 통신만 검증.

from __future__ import annotations

import os
import sys

# 프로젝트 루트를 path에 추가
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 환경변수만 사용 (dotenv은 로컬 .env용, 키는 Windows 환경변수 우선)
try:
    from backend.app.core.env_keys import (
        get_fred_api_key,
        get_llm_openai_key,
        get_llm_gemini_key,
        get_kis_app_key,
        get_kis_app_secret,
        get_dart_api_key,
    )
except Exception as e:
    print("[FAIL] import env_keys:", e)
    sys.exit(2)


def check_fred() -> str:
    key = get_fred_api_key()
    if not key:
        return "SKIP (FRED_API_KEY not set)"
    try:
        import requests
        r = requests.get(
            "https://api.stlouisfed.org/fred/series",
            params={"series_id": "GDP", "api_key": key, "file_type": "json"},
            timeout=10,
        )
        if r.status_code == 200:
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def check_openai() -> str:
    key = get_llm_openai_key()
    if not key:
        return "SKIP (OPENAI_API_KEY not set)"
    try:
        import requests
        r = requests.get(
            "https://api.openai.com/v1/models",
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        if r.status_code == 200:
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def check_gemini() -> str:
    key = get_llm_gemini_key()
    if not key:
        return "SKIP (GEMINI_API_KEY / GOOGLE_API_KEY not set)"
    # Try current model names (Google AI for Developers endpoint)
    for model in ("gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-latest", "gemini-pro"):
        try:
            import requests
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
                json={"contents": [{"parts": [{"text": "Hi"}]}]},
                timeout=15,
            )
            if r.status_code in (200, 201):
                return "OK"
            if r.status_code == 429:
                return "OK (rate limited)"
            if r.status_code != 404:
                return f"FAIL (HTTP {r.status_code})"
        except Exception as e:
            return f"FAIL ({e})"
    return "FAIL (no model available)"


def check_kis() -> str:
    key = get_kis_app_key()
    secret = get_kis_app_secret()
    if not key or not secret:
        return "SKIP (KIS_APP_KEY / KIS_APP_SECRET not set)"
    try:
        import requests
        # KIS 토큰 발급 (모의투자 또는 실전 URL)
        r = requests.post(
            "https://openapivts.koreainvestment.com:29443/oauth2/tokenP",
            json={
                "grant_type": "client_credentials",
                "appkey": key,
                "appsecret": secret,
            },
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        if r.status_code == 200 and r.json().get("access_token"):
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def main() -> int:
    print("Aegis-X v3 — External API connectivity (keys from Windows env)")
    print("-" * 50)
    results = []
    results.append(("FRED (macro)", check_fred()))
    results.append(("OpenAI (LLM)", check_openai()))
    results.append(("Gemini (LLM)", check_gemini()))
    results.append(("KIS (broker)", check_kis()))
    for name, status in results:
        print(f"  {name}: {status}")
    print("-" * 50)
    fails = [n for n, s in results if s.startswith("FAIL")]
    if fails:
        print("Fix failing entries or set env vars. See docs/ENV_Windows11_API_Keys.md")
        return 1
    print("All checked endpoints OK or SKIP (key not set).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
