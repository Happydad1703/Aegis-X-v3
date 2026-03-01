02_System_Architecture_SAD.md
Document ID: AEGIS-X-SAD-v1.0
________________________________________
1. Logical Architecture
External APIs
    ↓
Data Ingestion Layer
    ↓
Regime Engine (Hybrid AI)
    ↓
Allocation Engine
    ↓
Risk Engine
    ↓
Fleet Execution
    ↓
Learning Engine
    ↓
Capital Optimizer
    ↓
Meta-Control
    ↓
Self-Healing
    ↓
Governance
________________________________________
2. Physical Components
•	Python Application Core
•	PostgreSQL
•	Ledger NDJSON
•	state_ledger.json
•	FastAPI endpoints
•	ScanScheduler
•	Twin Simulation Engine
________________________________________
3. Deployment Model
•	Single-node (초기)
•	Dockerized 환경 가능
•	향후 Multi-Process 확장 가능
