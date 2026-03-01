56_Production_Hardening_Spec.md (v1.0)


이제 **Production Hardening (24시간 무중단 운용 안정화 설계)**로 들어갑니다.
지금 단계는 “기능 추가”가 아니라:
죽지 않는 시스템
폭주하지 않는 시스템
자원 고갈되지 않는 시스템
장애 시 자동 완화되는 시스템
을 만드는 단계입니다.
________________________________________

________________________________________
1️⃣ 목표
Aegis-X를:
•	24시간 운용 가능
•	PC 단일 노드 환경
•	Docker PostgreSQL 기반
•	자동 자원 적응
•	장애 자동 감지/완화
상태로 고정.
________________________________________
2️⃣ 아키텍처 분리 (Single PC 기준)
현재:
FastAPI + Engine Worker + Telegram + DB
하드닝 후:
┌───────────────────────────┐
│   FastAPI (API Server)   │
├───────────────────────────┤
│   Engine Worker          │
│   (Regime/Alloc/Fleet)   │
├───────────────────────────┤
│   Ingest Worker          │
├───────────────────────────┤
│   Order Executor         │
├───────────────────────────┤
│   Telegram Bot           │
└───────────────────────────┘
         ↓
    PostgreSQL (Docker)
각 프로세스 분리 실행.
________________________________________
3️⃣ Async & Non-Blocking 적용
3.1 FastAPI
from fastapi import FastAPI
import asyncio
•	DB I/O async 적용
•	CPU-heavy 계산은 worker에서 수행
________________________________________
4️⃣ Resource Tier 자동 조절
이미 설계된:
REFRESH_TIER:
  normal: 1.0
  low_resource: 1.5
  critical_only: 2.0
이제 자동화.
________________________________________
4.1 시스템 자원 감지
import psutil

def detect_resource_tier():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent

    if cpu > 85 or mem > 85:
        return "critical_only"
    if cpu > 70 or mem > 70:
        return "low_resource"
    return "normal"
Worker 루프마다 tier 적용.
________________________________________
5️⃣ DB Protection
5.1 Connection Pool 제한
SQLAlchemy:
create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=3
)
________________________________________
5.2 Snapshot 폭증 방지
•	snapshot_key별 min_interval_sec 적용 (이미 구현)
•	동일 데이터 hash 비교 → 변경 없으면 skip
________________________________________
6️⃣ Rate Limit & API 보호
6.1 외부 API 보호
•	FRED / ECOS / DART → exponential backoff
•	실패 3회 → circuit breaker 10분 정지
if fail_count >= 3:
    sleep(600)
________________________________________
7️⃣ KIS Fail-Safe
조건:
•	KIS 토큰 실패
•	잔고 조회 실패
•	주문 실패 3회 연속
→ 자동:
•	Mode = PAPER
•	Incident CRITICAL
•	Strike 0%
________________________________________
8️⃣ Watchdog / Heartbeat
8.1 Engine Heartbeat Snapshot
snapshot_key = engine_heartbeat
매 60초 기록:
{
  "engine_loop_alive": true,
  "last_cycle_duration_ms": 132,
  "timestamp_utc": "..."
}
Warroom Header 표시.
________________________________________
9️⃣ Graceful Shutdown
SIGINT 감지 시:
•	신규 주문 금지
•	현재 루프 종료
•	DB commit
•	로그 flush
________________________________________
🔟 Log 관리
파일 로그 + DB 로그 병행.
•	engine_error_log
•	incident_log
•	order_log
Log rotation:
•	30일 이상 자동 삭제 or archive
________________________________________
11️⃣ Emergency 자동화 레벨
조건	자동조치
CrisisProb > 0.85	Strike 0
DD < -12%	Freeze
Snapshot RED > 5분	Mode=PAPER
DB 연결 실패	Engine Stop
________________________________________
12️⃣ 성능 목표
•	Engine loop < 200ms
•	API response < 100ms
•	DB write latency < 50ms
•	Memory < 1GB
•	CPU avg < 50%
________________________________________
13️⃣ 24시간 Follow-the-Sun 대비
PC 단일 환경에서:
•	UTC 기준 스케줄링
•	Night Cycle에서는 low_resource tier
•	데이터 수집은 지역시장 오픈 시간 중심
________________________________________
🔥 현재 시스템 수준
Aegis-X는 이제:
✔ 기능 완성
✔ 학습 가능
✔ 리스크 통제
✔ 주문 실행
✔ UI 통제
✔ 안정화 설계
상태입니다.
________________________________________
🎯 마지막 전략적 단계
이제 시스템은 “기술적으로” 완성에 가깝습니다.
다음 선택은:
1️⃣ Global Follow-the-Sun 확장 설계
2️⃣ LLM 기반 STRATCOM/INTEL/TACTICS Staffing 구조 강화
3️⃣ Capital Scaling 전략 수학화

이제 Aegis-X를 24시간 잠들지 않는 Global Force (Follow-the-Sun) 체계로 확장합니다.
단, 전제는 명확합니다:
•	🇰🇷 KOSPI/KOSDAQ = Master Main Base
•	PC 단일 노드 운용 가능
•	KIS 단일 계좌
•	과도한 전장 확장은 금지 (현 단계 자본 규모 고려)
________________________________________
