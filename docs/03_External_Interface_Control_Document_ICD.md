03_External_Interface_Control_Document_ICD.md
Document ID: AEGIS-X-ICD-v1.0
________________________________________
1. External Data Source Inventory
(요청하신 뉴스/공시/자료 소스 정식 통합)
1.1 뉴스 소스
Source	Storage	Refresh
Naver	Ledger	3 min
Daum	Ledger	5 min
Yonhap RSS	Ledger	5 min
Edaily RSS	Ledger	5 min
Finnhub	Ledger	5 min
Alpha Vantage	Ledger	12 min
1.2 공시
Source	Storage
DART	Ledger + macro_context
SEC EDGAR	Ledger
1.3 매크로
Source	Storage
FRED	macro_context
ECOS	macro_context
1.4 브로커
Source	Storage
KIS	state_ledger.json
________________________________________
2. API Failure Handling
API	Retry	Fallback
FRED	3x backoff	이전 데이터 유지
ECOS	3x	이전 값 유지
DART	2x	공시 지연 경고
뉴스	Skip	Regime confidence 감소
KIS	3x	신규 진입 중단
________________________________________
3. US Market (미국 시장) — V3 확장
3.1 결제·거래 일정
•	**Settlement**: T+2 (미국 주식 결제일: 체결일+2 영업일). 캘린더 로직은 UTC 기준, NYSE/NASDAQ 휴장일 반영 권장.
•	**서머타임(DST)**: 미국 동부(ET)는 3월 둘째 일요일~11월 첫 일요일 EDT(UTC-4), 그 외 EST(UTC-5). 시세·공시 타임스탬프 변환 시 timezone 명시 필수.
3.2 미국 시장 데이터 소스
Source	Storage	Refresh	용도	환경변수
Yahoo Finance (RapidAPI)	ext_event_raw / 시세 캐시	5~15 min	미국 주식 시세, 차트	RAPIDAPI_KEY (apidojo/yahoo-finance1)
Polygon.io	ext_event_raw / 시세	1~5 min	실시간/지연 시세, 뉴스	POLYGON_API_KEY
Alpha Vantage	Ledger / ext_event_raw	12 min	시세·뉴스·매크로	ALPHA_VANTAGE_API_KEY
FRED	macro_context	1 hour	미국 매크로(금리·GDP 등)	FRED_API_KEY
SEC EDGAR	Ledger	일/배치	공시	(선택)
3.3 미국 소스 Failure Handling
API	Retry	Fallback
Yahoo (RapidAPI)	2x backoff	이전 캐시 유지, Regime confidence 감소
Polygon	3x backoff	이전 시세 유지
Alpha Vantage	3x (5 calls/min 제한 고려)	이전 데이터 유지
FRED	3x backoff	이전 데이터 유지
3.4 ICD 연동 모듈 (V3)
•	ingest_worker: FRED/Alpha Vantage 이벤트 → ext_event_raw. (Yahoo/Polygon 확장 시 동일 테이블, source_name 구분.)
•	check_comm.py: FRED 검증 필수. Yahoo/Polygon/Alpha Vantage는 확장 시 통신점검 항목 추가.
•	시간 처리: 모든 저장은 UTC (TIMESTAMPTZ). 미국 시장 표시용으로만 ET 변환.
________________________________________
참조: docs/Yahoo_RapidAPI_연동.md, docs/외부기관_목록_및_통신점검.md, env_keys.py
