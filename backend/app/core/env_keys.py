# core/env_keys.py — SE-17, 16_Config: API Key는 Windows 11 환경변수에서만 획득
# 코드/파일에 키 하드코딩 금지. 모든 외부 기관(뉴스/정보원, LLM, KIS) 통신은 여기서 키 조회.

from __future__ import annotations

import os
from typing import Optional

# -----------------------------------------------------------------------------
# 환경변수 이름 상수 (Windows 11 시스템 환경변수에 설정)
# -----------------------------------------------------------------------------

# DB (로컬 .env에서도 로드 가능하나, 운영은 환경변수 권장)
ENV_DATABASE_URL = "DATABASE_URL"
ENV_ASYNC_DATABASE_URL = "ASYNC_DATABASE_URL"

# 뉴스/정보원
ENV_FRED_API_KEY = "FRED_API_KEY"
ENV_ECOS_API_KEY = "ECOS_API_KEY"  # 한국 선행지표 등
ENV_DART_API_KEY = "DART_API_KEY"   # 전자공시
ENV_NAVER_CLIENT_ID = "NAVER_CLIENT_ID"
ENV_NAVER_CLIENT_SECRET = "NAVER_CLIENT_SECRET"
ENV_FINNHUB_API_KEY = "FINNHUB_API_KEY"
ENV_ALPHA_VANTAGE_API_KEY = "ALPHA_VANTAGE_API_KEY"

# LLM
ENV_OPENAI_API_KEY = "OPENAI_API_KEY"
ENV_ANTHROPIC_API_KEY = "ANTHROPIC_API_KEY"  # Claude
ENV_GOOGLE_API_KEY = "GOOGLE_API_KEY"       # Gemini
ENV_GEMINI_API_KEY = "GEMINI_API_KEY"        # Gemini (별도 키명)
ENV_DEEPSEEK_API_KEY = "DEEPSEEK_API_KEY"

# KIS (한국투자증권)
ENV_KIS_APP_KEY = "KIS_APP_KEY"
ENV_KIS_APP_SECRET = "KIS_APP_SECRET"

# Push 알림 (Telegram / Kakao)
ENV_TELEGRAM_BOT_TOKEN = "TELEGRAM_BOT_TOKEN"
ENV_TELEGRAM_CHAT_ID = "TELEGRAM_CHAT_ID"
ENV_KAKAO_REST_KEY = "KAKAO_REST_KEY"  # Kakao 알림용 (선택)


def get_env(key: str, default: Optional[str] = None) -> Optional[str]:
    """Windows 환경변수에서 값 조회. 빈 문자열은 None으로 취급."""
    v = os.environ.get(key, default or "")
    return (v or None) if isinstance(v, str) and v.strip() else (default if default else None)


def get_api_key(key_env: str) -> Optional[str]:
    """API 키 전용: 환경변수에서만 읽음. 키는 코드/리포에 저장 금지."""
    return get_env(key_env)


# -----------------------------------------------------------------------------
# 외부 기관별 키 조회 (통신 확립 시 사용)
# -----------------------------------------------------------------------------

def get_fred_api_key() -> Optional[str]:
    return get_api_key(ENV_FRED_API_KEY)


def get_llm_openai_key() -> Optional[str]:
    return get_api_key(ENV_OPENAI_API_KEY)


def get_llm_gemini_key() -> Optional[str]:
    return get_api_key(ENV_GEMINI_API_KEY) or get_api_key(ENV_GOOGLE_API_KEY)


def get_llm_claude_key() -> Optional[str]:
    return get_api_key(ENV_ANTHROPIC_API_KEY)


def get_llm_deepseek_key() -> Optional[str]:
    return get_api_key(ENV_DEEPSEEK_API_KEY)


def get_kis_app_key() -> Optional[str]:
    return get_api_key(ENV_KIS_APP_KEY)


def get_kis_app_secret() -> Optional[str]:
    return get_api_key(ENV_KIS_APP_SECRET)


def get_dart_api_key() -> Optional[str]:
    return get_api_key(ENV_DART_API_KEY)


def get_ecos_api_key() -> Optional[str]:
    return get_api_key(ENV_ECOS_API_KEY)


def get_naver_client_id() -> Optional[str]:
    return get_api_key(ENV_NAVER_CLIENT_ID)


def get_naver_client_secret() -> Optional[str]:
    return get_api_key(ENV_NAVER_CLIENT_SECRET)


def get_finnhub_api_key() -> Optional[str]:
    return get_api_key(ENV_FINNHUB_API_KEY)


def get_alpha_vantage_api_key() -> Optional[str]:
    return get_api_key(ENV_ALPHA_VANTAGE_API_KEY)


def get_telegram_bot_token() -> Optional[str]:
    return get_api_key(ENV_TELEGRAM_BOT_TOKEN)


def get_telegram_chat_id() -> Optional[str]:
    return get_env(ENV_TELEGRAM_CHAT_ID)
