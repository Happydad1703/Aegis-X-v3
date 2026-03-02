# 뉴스/공시/자료원 수집 및 DB 기록 검증

통신점검 완료한 **모든** 뉴스·공시·자료원에서 자료를 획득하고, `ext_event_raw`에 기록되는지 확인하는 방법입니다.

---

## 1. 수집 대상 (ingest_worker → event_repo → ext_event_raw)

| source_name   | event_type | 환경변수 / 비고 |
|---------------|------------|------------------|
| ingest_worker | heartbeat  | 없음 (항상 1건) |
| FRED          | macro      | FRED_API_KEY |
| ECOS          | macro      | ECOS_API_KEY |
| DART          | disclosure | DART_API_KEY |
| Naver         | news       | NAVER_CLIENT_ID, NAVER_CLIENT_SECRET |
| Yonhap        | news       | 없음 (연합뉴스 RSS) |
| Edaily        | news       | 없음 (이데일리 RSS) |
| Finnhub       | quote      | FINNHUB_API_KEY |
| AlphaVantage  | quote      | ALPHA_VANTAGE_API_KEY |

- **단일 기록 경로**: 모든 삽입은 `core/event_repo.py` → `ext_event_raw` 만 사용합니다.
- 키가 없으면 해당 소스는 건너뛰고(0건), 오류 시에도 다른 소스는 계속 수집합니다.

---

## 2. 사전 조건

- DB 마이그레이션 적용: `.\scripts\migrate_db.ps1`  
  → `ext_event_raw` 테이블이 있어야 합니다.
- `.env` 또는 시스템 환경변수에 `DATABASE_URL` 설정.

---

## 3. 1회 수집 실행

```powershell
cd D:\AEGIS-X_v3
python scripts/run_ingest_cycle.py
```

- 출력 예: `[OK] ingest cycle done, inserted=N rows into ext_event_raw`
- N = 이번 사이클에 삽입된 행 수 (heartbeat + 키가 설정된 소스들).

---

## 4. DB 기록 여부 확인

### 방법 A: 검증 스크립트 (권장)

```powershell
# 수집 없이 현재 DB만 조회
python scripts/verify_ingest_db.py

# 수집 1회 실행 후 바로 검증
python scripts/verify_ingest_db.py --run-ingest
```

- `ext_event_raw`를 `source_name`, `event_type`별로 집계해 **건수**와 **최신 수신 시각**을 출력합니다.
- `ext_event_raw` 테이블이 없으면 마이그레이션 실행을 안내합니다.

### 방법 B: 직접 SQL

```sql
SELECT source_name, event_type, COUNT(*) AS cnt, MAX(received_at) AS latest
FROM ext_event_raw
GROUP BY source_name, event_type
ORDER BY source_name, event_type;
```

---

## 5. 정상 동작 기준

- `run_ingest_cycle.py` 실행 후 `inserted >= 1` (최소 heartbeat 1건).
- `verify_ingest_db.py` 실행 시 `source_name`/`event_type`별로 행이 보이고, 최근 수집한 시간이 `latest`에 반영됨.
- 환경변수가 설정된 소스는 각각 주기적으로 행이 증가하는지 확인하면 됩니다.

이를 통해 **통신점검 완료한 모든 뉴스/공시/자료원에서 자료를 획득하고, 해당 자료가 DB(ext_event_raw)에 기록되는지** 확인할 수 있습니다.
