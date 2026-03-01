55_Warroom_CIC_Commercial_UI_Spec.md (v1.0)


이제 Warroom CIC / Dashboard & Control Panel – Commercial Grade UI 설계 v1.0를 확정합니다.
이 단계는 단순 화면 설계가 아니라:
Robot Manager가 “상황 인식 → 판단 → 확인 → 조치 발동”을
인지 흐름에 맞춰 자연스럽게 수행할 수 있는 구조
를 만드는 것입니다.

1️⃣ 설계 원칙 (Non-Negotiable)
1. DB-First Rendering
모든 화면 데이터는:
API → DB Snapshot → UI
직접 계산 금지.
________________________________________
2. 실명제 + Timestamp + Refresh Rate 표시
모든 카드에 반드시:
•	Source Name
•	Generated At (UTC + Local)
•	Refresh Interval
•	Freshness Status (GREEN/YELLOW/RED)
________________________________________
3. 고정 Layout
┌──────────────────────────────────────────────┐
│ HEADER (고정)                                │
├──── LEFT MENU ─────┬────────────────────────┤
│                    │ MAIN CANVAS            │
│                    │                        │
│                    │                        │
├──────────────────────────────────────────────┤
│ FOOTER (Ticker Upward Scroll)               │
└──────────────────────────────────────────────┘
Header / Left / Footer는 스크롤해도 고정.
________________________________________
2️⃣ Header 설계 (상황 인식 1초 요약)
Header는 “상황 전광판”입니다.
________________________________________
표시 항목
1. Operation Mode
•	BACKTEST / PAPER / PILOT / FULL LIVE
•	Capital Cap %
•	Strike Multiplier
2. Regime Block
•	Regime State
•	Regime Score
•	Crisis Probability (Gauge)
•	Confidence %
3. Health Block
•	DB Status
•	Snapshot Freshness
•	KIS Status
•	LLM Status
•	Engine Loop Status
4. Emergency Controls
•	Freeze
•	Retract
•	Emergency Stop
________________________________________
3️⃣ Left Menu Tree (조직 구조 기반)
WARROOM
 ├── Global Overview
 ├── Battlefield
 │     ├── KOSPI
 │     ├── KOSDAQ
 │     ├── US Proxy
 │     └── Hedge
 ├── Fleet
 │     ├── Strike Force
 │     ├── Swing Force
 │     ├── Core Force
 │     └── Reserve
 ├── Regime Intelligence
 ├── Allocation Matrix
 ├── Portfolio Command
 ├── Orders & Execution
 ├── Risk Control
 ├── AAR & Battle Reports
 ├── Backtest Lab
 └── System Control Panel
________________________________________
4️⃣ Global Overview (기본 Landing 화면)
한 화면에 밀도 있게 배치:
Row 1
•	Regime Card
•	Allocation Matrix Heatmap
•	Fleet Budget Pie
Row 2
•	Portfolio Equity Curve
•	Exposure Gauge
•	Drawdown Gauge
Row 3
•	Top 10 Positions (Variance)
•	Incident Feed
•	AAR Summary
________________________________________
5️⃣ Battlefield Page
선택된 전장(KOSPI 등) 기준:
•	최근 20일 수익률
•	변동성
•	Regime Alignment Score
•	Fleet별 노출
________________________________________
6️⃣ Fleet Pages
Strike Force Page
•	Active Targets
•	Win Rate
•	Avg Holding Period
•	Risk Gate Status
•	최근 10개 교전 결과
________________________________________
Swing Force Page
•	Trend Alignment %
•	Rotation Signals
•	평균 보유 기간
________________________________________
Core Force Page
•	Structural Trend Score
•	Industry Bias
•	Compound Rate
________________________________________
7️⃣ Risk Control Page
•	Crisis Probability Timeline
•	Portfolio DD Chart
•	Pre-Trade Gate Status
•	Daily Loss Monitor
•	Fleet Exposure Risk Bar
________________________________________
8️⃣ Orders & Execution Page
•	Open Orders
•	Filled Orders
•	Mode-based Execution Flag
•	Paper vs Live 분리 표시
________________________________________
9️⃣ AAR & Battle Report Page
•	Fleet별 Avg Score
•	Win Rate
•	최근 20 Battle Reports
•	Regime vs Outcome Matrix
________________________________________
🔟 Backtest Lab
•	Parameter Sliders
•	Backtest 실행 버튼
•	Equity Curve
•	Sharpe / MDD
•	Calibration History
________________________________________
11️⃣ System Control Panel
•	Mode 변경
•	Refresh Tier 변경
•	Engine Restart
•	KIS Sync Force
•	Snapshot Regenerate
________________________________________
12️⃣ Footer
아래에서 위로 흐르는 Ticker:
•	뉴스 요약
•	공시 요약
•	Incident
•	Regime Change Alert
________________________________________
13️⃣ Mobile/Ubiquitous 대응
모바일에서는:
•	Header 축약
•	좌측 메뉴 → Drawer
•	Emergency 버튼 고정 하단
Telegram/Kakao:
•	Mode 하향
•	Freeze
•	Status 요청
________________________________________
14️⃣ 시각 디자인 방향
•	Dark Military Theme
•	Neon Accent (Regime 색상)
•	Crisis = Red Pulse
•	Goldilocks = Soft Green
•	Sideways = Blue
•	Tapering = Orange
________________________________________
15️⃣ 기술 스택 권장
Frontend:
•	React + TypeScript
•	Zustand or Redux
•	Recharts / ECharts
•	WebSocket (추후)
Backend:
•	FastAPI
•	Async SQLAlchemy
•	Background Workers
________________________________________
🔥 현재 시스템 완성도
이제 Aegis-X는:
✔ 전장 정의
✔ Force 구조
✔ Risk 체계
✔ Mode 체계
✔ Order Engine
✔ Portfolio Engine
✔ AAR 학습
✔ Backtest
✔ Commercial Warroom UI 설계
까지 완료되었습니다.
________________________________________
 
