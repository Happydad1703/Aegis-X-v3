01_Stakeholder_Requirements_SRS.md
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
