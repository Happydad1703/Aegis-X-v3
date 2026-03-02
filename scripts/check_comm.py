# scripts/check_comm.py — SE-05, 14_TVP: 외부 기관(뉴스/정보원, LLM, KIS) API 키·통신 확인
# 모든 API Key는 Windows 11 환경변수에서 획득. 환경변수에서 읽어 통신만 검증.

from __future__ import annotations

import os
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가 및 .env 로드 (안정성 점검 시 동일 환경 보장)
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except Exception:
    pass

# 환경변수만 사용 (dotenv은 로컬 .env용, 키는 Windows 환경변수 우선)
try:
    from backend.app.core.env_keys import (
        get_fred_api_key,
        get_llm_openai_key,
        get_llm_gemini_key,
        get_llm_claude_key,
        get_llm_deepseek_key,
        get_kis_app_key,
        get_kis_app_secret,
        get_dart_api_key,
        get_ecos_api_key,
        get_naver_client_id,
        get_naver_client_secret,
        get_finnhub_api_key,
        get_alpha_vantage_api_key,
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
    try:
        import requests
        # 모델 목록 조회로 키 유효성 검사 (모델명 변경에 강함)
        r = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            params={"key": key},
            timeout=15,
        )
        if r.status_code == 200:
            data = r.json()
            if data.get("models"):
                return "OK"
            return "OK (no models in response)"
        if r.status_code == 429:
            return "OK (rate limited)"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def check_anthropic() -> str:
    key = get_llm_claude_key()
    if not key:
        return "SKIP (ANTHROPIC_API_KEY not set)"
    try:
        import requests
        r = requests.get(
            "https://api.anthropic.com/v1/models",
            headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
            timeout=10,
        )
        if r.status_code == 200:
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def check_deepseek() -> str:
    key = get_llm_deepseek_key()
    if not key:
        return "SKIP (DEEPSEEK_API_KEY not set)"
    try:
        import requests
        r = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": [{"role": "user", "content": "Hi"}], "max_tokens": 5},
            timeout=15,
        )
        if r.status_code == 200:
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def check_dart() -> str:
    key = get_dart_api_key()
    if not key:
        return "SKIP (DART_API_KEY not set)"
    try:
        import requests
        from datetime import datetime
        today = datetime.utcnow().strftime("%Y%m%d")
        r = requests.get(
            "https://opendart.fss.or.kr/api/list.json",
            params={"crtfc_key": key, "page_no": 1, "page_count": 1, "bgn_de": today, "end_de": today},
            timeout=10,
        )
        if r.status_code == 200:
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def check_ecos() -> str:
    key = get_ecos_api_key()
    if not key:
        return "SKIP (ECOS_API_KEY not set)"
    try:
        import requests
        # StatisticTableList: 통계 테이블 목록 조회 (가벼운 검증)
        r = requests.get(
            "https://ecos.bok.or.kr/api/StatisticTableList/"
            f"{key}/json/kr/1/10/",
            timeout=10,
        )
        if r.status_code == 200:
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def check_naver() -> str:
    cid = get_naver_client_id()
    secret = get_naver_client_secret()
    if not cid or not secret:
        return "SKIP (NAVER_CLIENT_ID / NAVER_CLIENT_SECRET not set)"
    try:
        import requests
        r = requests.get(
            "https://openapi.naver.com/v1/search/news.json",
            params={"query": "증권"},
            headers={"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": secret},
            timeout=10,
        )
        if r.status_code == 200:
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def check_yonhap_rss() -> str:
    """연합뉴스 RSS (키 불필요, 연결만 확인)."""
    try:
        import requests
        r = requests.get("https://www.yna.co.kr/rss/economy.xml", timeout=10)
        if r.status_code == 200:
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def check_edaily_rss() -> str:
    """이데일리 RSS (키 불필요, 연결만 확인)."""
    try:
        import requests
        r = requests.get("https://www.idailynews.co.kr/rss/allArticle.xml", timeout=10)
        if r.status_code == 200:
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def check_finnhub() -> str:
    key = get_finnhub_api_key()
    if not key:
        return "SKIP (FINNHUB_API_KEY not set)"
    try:
        import requests
        r = requests.get(
            "https://finnhub.io/api/v1/quote",
            params={"symbol": "AAPL", "token": key},
            timeout=15,
        )
        if r.status_code == 200:
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


def check_alpha_vantage() -> str:
    key = get_alpha_vantage_api_key()
    if not key:
        return "SKIP (ALPHA_VANTAGE_API_KEY not set)"
    try:
        import requests
        r = requests.get(
            "https://www.alphavantage.co/query",
            params={"function": "GLOBAL_QUOTE", "symbol": "AAPL", "apikey": key},
            timeout=15,
        )
        if r.status_code == 200:
            return "OK"
        return f"FAIL (HTTP {r.status_code})"
    except Exception as e:
        return f"FAIL ({e})"


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
    results.append(("ECOS (macro)", check_ecos()))
    results.append(("DART (공시)", check_dart()))
    results.append(("Naver (뉴스/검색)", check_naver()))
    results.append(("연합뉴스 RSS", check_yonhap_rss()))
    results.append(("이데일리 RSS", check_edaily_rss()))
    results.append(("Finnhub (뉴스/시세)", check_finnhub()))
    results.append(("Alpha Vantage (시세/뉴스)", check_alpha_vantage()))
    results.append(("OpenAI (LLM)", check_openai()))
    results.append(("Anthropic (LLM)", check_anthropic()))
    results.append(("Gemini (LLM)", check_gemini()))
    results.append(("DeepSeek (LLM)", check_deepseek()))
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
