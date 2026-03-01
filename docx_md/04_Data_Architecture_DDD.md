04_Data_Architecture_DDD.md
Document ID: AEGIS-X-DDD-v1.0
________________________________________
1. Data Flow
External → Ingest → Ledger/macro_context → Regime → Allocation → Risk → Execution
________________________________________
2. Storage Classification
Data Type	Location
NEWS_EVENT	Ledger NDJSON
DART_EVENT	Ledger NDJSON
SEC_EVENT	Ledger NDJSON
macro_context	PostgreSQL
regime_status	PostgreSQL
strategy_log	PostgreSQL
state_ledger	JSON File
________________________________________
3. SSOT 정의
Domain	SSOT
Market Events	Ledger
Macro	macro_context
Positions	state_ledger


 
