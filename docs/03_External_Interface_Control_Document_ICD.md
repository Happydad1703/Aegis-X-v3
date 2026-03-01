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
