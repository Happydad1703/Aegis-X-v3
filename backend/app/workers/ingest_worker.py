# workers/ingest_worker.py — SE-03 ICD, 04 DDD: 외부 소스 → ext_event_raw (event_repo 경유)
# 통신점검 완료한 모든 뉴스/공시/자료원에서 자료 획득 후 event_repo로만 DB 기록.

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

from backend.app.core.db import SessionLocal
from backend.app.core.env_keys import (
    get_fred_api_key,
    get_ecos_api_key,
    get_dart_api_key,
    get_naver_client_id,
    get_naver_client_secret,
    get_finnhub_api_key,
    get_alpha_vantage_api_key,
)
from backend.app.core.event_repo import insert_raw_event_sync


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ingest_heartbeat_sync() -> int:
    """Minimal source: heartbeat. Ensures ext_event_raw has rows (no API key required)."""
    db = SessionLocal()
    try:
        insert_raw_event_sync(
            db,
            source_name="ingest_worker",
            event_type="heartbeat",
            payload={"ts_utc": _now_utc(), "source": "heartbeat"},
        )
        return 1
    finally:
        db.close()


def _ingest_fred_sync() -> int:
    """FRED 매크로 (FRED_API_KEY 필요)."""
    key = get_fred_api_key()
    if not key:
        return 0
    try:
        import urllib.request
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id=DFEDTARU&api_key={key}&file_type=json"
        with urllib.request.urlopen(url, timeout=10) as r:
            obj = json.loads(r.read().decode())
        obs = obj.get("observations", [])[:5]
        if not obs:
            return 0
        db = SessionLocal()
        try:
            insert_raw_event_sync(
                db,
                source_name="FRED",
                event_type="macro",
                payload={"series": "DFEDTARU", "observations": obs, "ts_utc": _now_utc()},
            )
            return 1
        finally:
            db.close()
    except Exception:
        return 0


def _ingest_ecos_sync() -> int:
    """ECOS 한국은행 통계 (ECOS_API_KEY 필요)."""
    key = get_ecos_api_key()
    if not key:
        return 0
    try:
        import urllib.request
        url = f"https://ecos.bok.or.kr/api/StatisticTableList/{key}/json/kr/1/10/"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = r.read().decode()
        # 응답이 리스트 또는 딕셔너리일 수 있음
        try:
            obj = json.loads(data) if data.strip() else []
        except json.JSONDecodeError:
            return 0
        db = SessionLocal()
        try:
            insert_raw_event_sync(
                db,
                source_name="ECOS",
                event_type="macro",
                payload={"raw": obj if isinstance(obj, list) else [obj], "ts_utc": _now_utc()},
            )
            return 1
        finally:
            db.close()
    except Exception:
        return 0


def _ingest_dart_sync() -> int:
    """DART 전자공시 (DART_API_KEY 필요)."""
    key = get_dart_api_key()
    if not key:
        return 0
    try:
        import urllib.request
        today = datetime.now(timezone.utc).strftime("%Y%m%d")
        url = f"https://opendart.fss.or.kr/api/list.json?crtfc_key={key}&page_no=1&page_count=10&bgn_de={today}&end_de={today}"
        with urllib.request.urlopen(url, timeout=10) as r:
            obj = json.loads(r.read().decode())
        if obj.get("status") != "000":
            return 0
        db = SessionLocal()
        try:
            insert_raw_event_sync(
                db,
                source_name="DART",
                event_type="disclosure",
                payload={"list": obj.get("list", []), "total_count": obj.get("total_count"), "ts_utc": _now_utc()},
            )
            return 1
        finally:
            db.close()
    except Exception:
        return 0


def _ingest_naver_news_sync() -> int:
    """Naver 뉴스 검색 (NAVER_CLIENT_ID, NAVER_CLIENT_SECRET 필요)."""
    cid = get_naver_client_id()
    secret = get_naver_client_secret()
    if not cid or not secret:
        return 0
    try:
        import urllib.request
        req = urllib.request.Request(
            "https://openapi.naver.com/v1/search/news.json?query=증권&display=5",
            headers={"X-Naver-Client-Id": cid, "X-Naver-Client-Secret": secret},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            obj = json.loads(r.read().decode())
        items = obj.get("items", [])[:5]
        db = SessionLocal()
        try:
            insert_raw_event_sync(
                db,
                source_name="Naver",
                event_type="news",
                payload={"items": items, "ts_utc": _now_utc()},
            )
            return 1
        finally:
            db.close()
    except Exception:
        return 0


def _parse_rss_items(raw_xml: str, max_items: int = 5) -> list[dict]:
    """RSS XML에서 제목/링크 추출."""
    out = []
    try:
        root = ET.fromstring(raw_xml)
        # RSS 2.0: channel/item
        for item in root.findall(".//item")[:max_items]:
            title = item.find("title")
            link = item.find("link")
            pub = item.find("pubDate")
            out.append({
                "title": title.text if title is not None else "",
                "link": link.text if link is not None else "",
                "pubDate": pub.text if pub is not None else "",
            })
    except Exception:
        pass
    return out


def _ingest_yonhap_rss_sync() -> int:
    """연합뉴스 RSS (키 불필요)."""
    try:
        import urllib.request
        with urllib.request.urlopen("https://www.yna.co.kr/rss/economy.xml", timeout=10) as r:
            raw = r.read().decode()
        items = _parse_rss_items(raw, 5)
        db = SessionLocal()
        try:
            insert_raw_event_sync(
                db,
                source_name="Yonhap",
                event_type="news",
                payload={"items": items, "count": len(items), "ts_utc": _now_utc()},
            )
            return 1
        finally:
            db.close()
    except Exception:
        return 0


def _ingest_edaily_rss_sync() -> int:
    """이데일리 RSS (키 불필요)."""
    try:
        import urllib.request
        with urllib.request.urlopen("https://www.idailynews.co.kr/rss/allArticle.xml", timeout=10) as r:
            raw = r.read().decode()
        items = _parse_rss_items(raw, 5)
        db = SessionLocal()
        try:
            insert_raw_event_sync(
                db,
                source_name="Edaily",
                event_type="news",
                payload={"items": items, "count": len(items), "ts_utc": _now_utc()},
            )
            return 1
        finally:
            db.close()
    except Exception:
        return 0


def _ingest_finnhub_sync() -> int:
    """Finnhub 시세/뉴스 (FINNHUB_API_KEY 필요)."""
    key = get_finnhub_api_key()
    if not key:
        return 0
    try:
        import urllib.request
        url = f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={key}"
        with urllib.request.urlopen(url, timeout=15) as r:
            obj = json.loads(r.read().decode())
        db = SessionLocal()
        try:
            insert_raw_event_sync(
                db,
                source_name="Finnhub",
                event_type="quote",
                payload={"symbol": "AAPL", "quote": obj, "ts_utc": _now_utc()},
            )
            return 1
        finally:
            db.close()
    except Exception:
        return 0


def _ingest_alpha_vantage_sync() -> int:
    """Alpha Vantage 시세 (ALPHA_VANTAGE_API_KEY 필요)."""
    key = get_alpha_vantage_api_key()
    if not key:
        return 0
    try:
        import urllib.request
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=AAPL&apikey={key}"
        with urllib.request.urlopen(url, timeout=15) as r:
            obj = json.loads(r.read().decode())
        db = SessionLocal()
        try:
            insert_raw_event_sync(
                db,
                source_name="AlphaVantage",
                event_type="quote",
                payload={"symbol": "AAPL", "quote": obj, "ts_utc": _now_utc()},
            )
            return 1
        finally:
            db.close()
    except Exception:
        return 0


def run_ingest_cycle_sync() -> int:
    """통신점검 완료한 모든 뉴스/공시/자료원에서 자료 획득 → ext_event_raw 기록. 반환: 이번 사이클 삽입 행 수."""
    n = 0
    n += _ingest_heartbeat_sync()
    n += _ingest_fred_sync()
    n += _ingest_ecos_sync()
    n += _ingest_dart_sync()
    n += _ingest_naver_news_sync()
    n += _ingest_yonhap_rss_sync()
    n += _ingest_edaily_rss_sync()
    n += _ingest_finnhub_sync()
    n += _ingest_alpha_vantage_sync()
    return n
