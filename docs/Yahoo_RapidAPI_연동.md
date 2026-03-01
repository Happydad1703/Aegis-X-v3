# Yahoo Finance (RapidAPI) 연동 (Aegis-X v3)

## 1. 개요

- **용도**: 미국/글로벌 종목 시세 조회 (AAPL, MSFT, NVDA 등)
- **환경 변수**: `RAPIDAPI_KEY` (RapidAPI 대시보드에서 발급)
- **API**: apidojo **yahoo-finance1** (호스트 `apidojo-yahoo-finance-v1.p.rapidapi.com`, 엔드포인트 `/market/get-quotes`)
- **v3 연동 시**: 키는 **Windows 11 환경변수**에만 설정. `backend/app/core/env_keys.py`에 `ENV_RAPIDAPI_KEY`, `get_rapidapi_key()` 추가 후, 통신 점검(`scripts/check_comm.py`) 및 시세 조회 모듈에서 사용.

**현재 v3 상태**: RAPIDAPI_KEY·Yahoo 시세 연동 코드 없음. 아래는 **연동 시** 적용할 명세.

---

## 2. 키 발급 및 등록

1. [RapidAPI - Yahoo Finance API (apidojo)](https://rapidapi.com/apidojo/api/yahoo-finance1) 접속
2. **Log In / Sign Up** (구글 연동 가능)
3. **Pricing** → **Basic (Free)** → **Start Free Plan** 클릭
4. **Endpoints** 탭 → **Header Parameters**에서 **X-RapidAPI-Key** 값 복사
5. Windows 11 환경변수 등록:
   ```powershell
   [Environment]::SetEnvironmentVariable("RAPIDAPI_KEY", "복사한_키_값", "User")
   ```
6. 터미널/IDE 재시작 후 `python scripts/check_comm.py` 실행 (Yahoo 점검 추가 시 **시세 Yahoo (RapidAPI): OK** 확인)

---

## 3. Basic 플랜 제약

| 항목 | 내용 |
|------|------|
| 요청 한도 | 월 500회 (Hard Limit) |
| Rate Limit | 초당 5회 |
| 권장 호출 주기 | 5~10분 간격 (장 중 1~2시간 간격도 가능) |

스케줄러를 너무 촘촘히 돌리면 한도가 빠르게 소진되므로, 시세 폴링은 **5분 이상 간격** 권장.

---

## 4. v3 연동 시 코드·경로

### 4.1 env_keys.py 추가

```python
# 시세 (RapidAPI Yahoo)
ENV_RAPIDAPI_KEY = "RAPIDAPI_KEY"

def get_rapidapi_key() -> Optional[str]:
    return get_api_key(ENV_RAPIDAPI_KEY)
```

### 4.2 시세 조회 (연동 시)

- **모듈 위치**: DB/HTTP 호출은 engines/ 밖에서만. 예: `backend/app/utils/yahoo_rapidapi.py` 또는 ingest/데이터 수집 전용 모듈.
- **사용 예** (연동 구현 시):

```python
# get_rapidapi_key()로 키 조회 후
# GET https://apidojo-yahoo-finance-v1.p.rapidapi.com/market/get-quotes
# Header: X-RapidAPI-Key: {key}
# 응답 → ext_event_raw 또는 engine_result 등 DB 경유 기록 (Single Write Path 준수)
```

- `RAPIDAPI_KEY`가 없거나 요청 실패 시 빈 리스트/None 반환. ICD: 뉴스/시세 실패 시 Skip, Regime confidence 감소 등 Fallback 정책 적용.

### 4.3 check_comm.py 추가 (선택)

- `check_yahoo_rapidapi()`: `get_rapidapi_key()`로 키 확인 후 `/market/get-quotes` 1회 요청, 200이면 OK.
- `main()`의 results에 `("Yahoo (RapidAPI 시세)", check_yahoo_rapidapi())` 추가.

---

## 5. 403 Forbidden 대응

- **구독 미활성화**: Pricing에서 **Start Free Plan** 반드시 클릭 후 사용
- **키 오류**: Endpoints 탭에서 **X-RapidAPI-Key** 다시 복사 후 `RAPIDAPI_KEY` 재등록
- **환경 반영**: 키 변경 후 터미널/VS Code 재시작

---

## 6. 연동 요약

| 항목 | v3 경로/이름 |
|------|----------------|
| 환경변수 | `RAPIDAPI_KEY` (env_keys에 추가 시 `ENV_RAPIDAPI_KEY`) |
| 통신 점검 | check_comm.py에 Yahoo RapidAPI 항목 추가 시 |
| 시세 조회 | 연동 시 전용 모듈 (utils 또는 ingest 연동), DB 기록은 repo 경유 |
| 저장소 | ext_event_raw / engine_result 등 (설계에 따라 결정) |

---

**참조 (v2)**: `AEGIS-X_v2/docs/Yahoo_RapidAPI_연동.md`  
**외부기관 목록**: `docs/외부기관_목록_및_통신점검.md` (시세 Yahoo RapidAPI 추가 시 해당 테이블 반영)
