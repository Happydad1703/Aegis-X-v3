# core/notifications.py — SE-32: 시장개시/종료, target 선정, 매매성립, 장 종결, AAR 등 주요 이벤트 시 Telegram/Kakao Push

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Optional

from backend.app.core.env_keys import get_telegram_bot_token, get_telegram_chat_id


def _send_telegram_impl(text: str) -> bool:
    token = get_telegram_bot_token()
    chat_id = get_telegram_chat_id()
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = json.dumps({"chat_id": chat_id, "text": text, "disable_web_page_preview": True}).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status == 200
    except Exception:
        return False


def send_telegram(message: str) -> bool:
    """Telegram으로 메시지 전송. 실패 시 False, 환경변수 미설정 시 무시."""
    try:
        return _send_telegram_impl(message[:4096])
    except Exception:
        return False


def send_kakao(message: str) -> bool:
    """Kakao Talk 알림 (스텁). 연동 시 env_keys + 여기 구현."""
    # TODO: Kakao API 연동 시 구현
    return False


def push_event(event_type: str, detail: str, channel: str = "telegram") -> bool:
    """
    주요 이벤트 푸시. event_type: market_open, market_close, target_selected, trade_filled, aar_done, freeze, retract, emergency_stop
    """
    msg = f"[Aegis-X] {event_type}: {detail}"
    if channel == "kakao":
        return send_kakao(msg)
    return send_telegram(msg)
