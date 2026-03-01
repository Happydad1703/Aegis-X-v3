Document ID: AEGIS-X-CHARTER-v1.0
Owner: Strategic Command (JCS)
Last Updated: 2026-XX-XX
________________________________________
1. System Purpose
Aegis-X는 다음을 목표로 하는 Autonomous Adaptive Capital Command System이다:
•	뉴스/공시/매크로 데이터를 기반으로 Market Regime를 분류
•	Regime에 따라 다자산 자본을 동적으로 배분
•	Fleet 단위 전략을 실행
•	Risk Engine을 통해 생존을 보장
•	Learning & Evolution을 통해 전략을 진화
•	Governance Layer를 통해 모든 의사결정을 추적·감사 가능하게 유지
________________________________________
2. System Objectives (정량 목표)
항목	목표
Target CAGR	15~25%
Max Portfolio DD	≤ 20%
Crisis Survival	Crisis 구간에서 손실 최소화
Audit Traceability	모든 전략 결정 100% 추적 가능
API Resilience	외부 API 장애 시 시스템 지속 운영
________________________________________
3. Operating Scope
자산군
•	Equity (KOSPI, KOSDAQ)
•	Fixed Income
•	FX (USD/KRW)
•	Commodity (WTI 등)
Regime 분류
•	Goldilocks
•	Sideways
•	Tapering
•	Crisis
________________________________________
4. Automation Level
영역	자동화 수준
Regime	Fully Autonomous
Allocation	Autonomous
Risk	Hard-Gated
Strategy Evolution	Proposal + Twin Validation
Governance	Mandatory Logging
________________________________________
5. External Dependencies (요약)
•	FRED, ECOS, DART
•	뉴스 6종
•	KIS Broker
•	PostgreSQL
•	LLM 4종 
📘 01_Stakeholder_Requirements_SRS.md
Document ID: AEGIS-X-SRS-v1.0
________________________________________
1. Functional Requirements
ID	Requirement
FR-001	System shall classify regime every 5 minutes.
FR-002	System shall record all external API calls.
FR-003	System shall not exceed defined risk caps.
FR-004	System shall generate AAR for every trade.
FR-005	System shall fallback to safe mode during systemic alarm.
________________________________________
2. Non-Functional Requirements
Category	Requirement
Availability	≥ 99% during trading hours
Data Integrity	Ledger append-only
Latency	Regime update ≤ 30 sec after data ingest
Security	API keys encrypted
Audit	100% decision traceability
________________________________________
3. Compliance Requirements
•	모든 결정은 Decision Object로 기록
•	Risk Mode 변경 시 Incident 기록
•	Strategy 변경 시 Meta Approval 기록
