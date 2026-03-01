# Cursor를 위한 최종 개발 전략

**목적**: Cursor에게 프로젝트 전체 맥락을 주입하고, 아키텍처 붕괴를 방지하기 위한 **Chain of Command** 및 Phase 0-1 착수 가이드, 지속적 재검증 루틴을 정의한다.

---

## 1. Chain of Command (아키텍처 봉인 원칙)

개발 시 **절대 위반 금지**. Cursor가 구조를 변경하거나 우회하지 않도록 명시한다.

| 원칙 | 내용 | 위반 시 |
|------|------|---------|
| **원칙 1 (DB-Only Read)** | 모든 UI와 상위 계층은 **engine_snapshot 테이블만 조회**해야 하며, **직접 계산을 수행해서는 안 됨**. | UI/API에서 engines 직접 호출 금지. Snapshot 조회만 허용. |
| **원칙 2 (Strict Module Boundary)** | **engines/** 내 모듈은 **순수 함수(dict in, dict out)** 여야 하며, **절대로 DB 세션이나 SQL을 포함해서는 안 됨**. | engines/ 에서 sqlalchemy, Session, text(), execute() 사용 금지. |
| **원칙 3 (Single Write Path)** | 모든 엔진 결과물은 **오직 core/snapshot_repo.py를 통해서만** DB에 기록되어야 함. | engine_worker만 snapshot_repo 호출. API/engines에서 직접 INSERT 금지. |

---

## 2. Phase 0-1 개발 착수 가이드 (Next Actions)

시뮬레이션 **GO** 확인 후, 아래 순서로 Cursor와 협업하여 코드를 완성한다.

| 단계 | 작업 내용 | 참조 SE 문서 |
|------|-----------|----------------|
| **0단계: 인프라** | `docker-compose up -d` 실행 및 `migrate_db.ps1`으로 스키마 생성 | SE-43, SE-64 |
| **1단계: Snapshot** | 보완된 `engine_worker.py`의 **6종 키** 산출 로직 최종 검증 | SE-44, SE-64 |
| **2단계: API** | `api/cic.py`에서 **snapshot_key 기반의 Read-only API** 구현 | SE-45, SE-65 |
| **3단계: UI** | Warroom Home 레이아웃에서 **6종 스냅샷 데이터** 렌더링 확인 | SE-46, SE-55 |

**6종 스냅샷 키 (Phase 0-1 정본)**: `engine_heartbeat`, `comm_health`, `regime_current`, `operation_mode`, `llm_status`, `risk_guard`

---

## 3. 지속적 재검증 (Continuous Validation) 루틴

기능 구현이 완료될 때마다 아래를 실행하여 구조·데이터 무결성을 유지한다.

| 항목 | 실행 방법 | 목적 |
|------|------------|------|
| **구조 점검** | `python scripts/internal_simulation.py` | 65번 아키텍처 잠금 상태 수시 확인 (디렉터리·DDL·Snapshot 6종·모듈 경계) |
| **데이터 무결성** | `pytest backend/tests/test_engine_loop.py` | 한 사이클 실행 후 DB에 6종 키가 정확히 들어오는지 확인 (사전: Postgres 기동, migrate, asyncpg 설치) |

---

## 4. 책임개발자 제언

- 현재 모든 준비가 완료되었습니다. Cursor에 폴더를 올리고 **「Phase 0: DB Schema 생성 및 마이그레이션 적용」** 부터 명령을 내리시면 됩니다.
- 개발 도중 **Regime 엔진의 실제 수학 모델링(SE-39)** 이나 **Pre-Trade Gate의 통제 로직(SE-50)** 등 특정 엔진의 세부 구현 알고리즘이 필요하시면 요청하시면, 정밀 설계 도면을 제공합니다.

---

## 5. 대화창 전환 시 맥락 유지 (권장)

일반 Chat(Ctrl+L)·Composer(Ctrl+I)는 **이전 대화 히스토리를 자동으로 이어받지 않습니다.**  
아래 방법으로 프로젝트 맥락을 유지하세요.

| 방법 | 설명 |
|------|------|
| **.cursorrules** | 프로젝트 루트에 Architecture Lock(SE-65)·DB-First·3원칙 명시 → **새 창을 열어도** AI가 항상 이 원칙을 전제로 대화. (이미 적용됨) |
| **@문서 첨부** | 새 대화 시작 시 **@docs/Context_Summary_For_New_Chat.md** 또는 **@docs/64_Phase0_1...**, **@docs/65_Final_Directory...** 등을 골뱅이로 첨부 → 이전에 확정한 SE 내용을 문서 기반으로 즉시 반영. |
| **지휘 지시문 재입력** | 새 단계를 시작할 때, **Context_Summary_For_New_Chat.md**의 "현재 단계 요약"을 복사해 붙여넣거나, 예: *"DB 마이그레이션은 완료되었고, 이제 Worker 6종 Snapshot 생성·API health 확인 단계이다"* 처럼 핵심 결론을 한 줄로 다시 알려 주기. |

**Context_Summary_For_New_Chat.md**: 확정 전제·Chain of Command·6종 키·현재 단계 요약을 한곳에 정리. 새 채팅 시 @ 또는 붙여넣기용.

---

## 6. 참조 문서

- **65_Final_Directory_Architecture_Lock_Spec.md** — 디렉터리 구조 변경 금지
- **64_Phase0_1_DB_and_MinWorker_Package_Spec.md** — DDL, Snapshot 6종, Worker
- **Context_Summary_For_New_Chat.md** — 새 대화 시 맥락 요약(지휘 지시문)
- **44_Snapshot_Key_Catalog_v1**, **45_API_Contract_v1** — 스냅샷 키·API 계약
- **System_Development_Framework.md**, **Internal_Simulation_Report.md** — 구도·시뮬레이션 결과
