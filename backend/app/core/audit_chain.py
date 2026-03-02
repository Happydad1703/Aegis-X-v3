# backend/app/core/audit_chain.py — 11_Governance_Audit_Spec: Immutable Hash Chain
# V2 로직 이식. 모든 결심(의사결정)의 투명성 확보. append-only, prev_hash/self_hash 체인.

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_AUDIT_ENABLED = os.getenv("AUDIT_CHAIN_ENABLED", "1").strip().lower() in ("1", "true", "yes")
# backend/app/core/audit_chain.py -> project root = parents[3]
_ROOT = Path(__file__).resolve().parents[3]
_AUDIT_FILE = _ROOT / "ssot" / "audit_chain.jsonl"
_LAST_HASH: Optional[str] = None


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _get_prev_hash() -> str:
    global _LAST_HASH
    if _LAST_HASH is not None:
        return _LAST_HASH
    if not _AUDIT_FILE.exists():
        return "genesis"
    last_line = None
    try:
        with open(_AUDIT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    last_line = line
    except Exception as e:
        logger.debug("audit_chain read tail: %s", e)
    if not last_line:
        return "genesis"
    try:
        rec = json.loads(last_line)
        prev = rec.get("self_hash", "genesis")
        _LAST_HASH = prev
        return prev
    except Exception:
        return "genesis"


def append_audit_event(
    event_type: str,
    payload: Dict[str, Any],
    payload_preview: Optional[str] = None,
) -> bool:
    """
    Immutable Hash Chain에 이벤트 1건 추가.
    event_type: regime | kill_switch | strategy_sync | allocation | emergency_stop | ...
    payload: 결심/이벤트 내용 (직렬화 가능한 dict). payload_hash로 저장.
    11_Governance_Audit_Spec: self_hash = SHA256(ts_utc|event_type|payload_hash|prev_hash).
    """
    global _LAST_HASH
    if not _AUDIT_ENABLED:
        return False
    try:
        ts_utc = datetime.now(timezone.utc).isoformat()
        payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        payload_hash = _sha256(payload_str)
        prev_hash = _get_prev_hash()
        content_to_hash = f"{ts_utc}|{event_type}|{payload_hash}|{prev_hash}"
        self_hash = _sha256(content_to_hash)
        rec = {
            "ts_utc": ts_utc,
            "event_type": event_type,
            "payload_hash": payload_hash,
            "prev_hash": prev_hash,
            "self_hash": self_hash,
            "payload_preview": (payload_preview or "")[:200],
        }
        _LAST_HASH = self_hash
        _AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(_AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return True
    except Exception as e:
        logger.warning("audit_chain append failed: %s", e)
        return False
