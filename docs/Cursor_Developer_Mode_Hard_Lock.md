# Aegis-X v3 — Cursor Developer Mode (Hard Architecture Lock)

## 0️⃣ 시스템 정체성

Aegis-X는:
- **Snapshot 기반 결정 시스템**이며
- 모든 의사결정은 **DB Snapshot을 통해서만** 흐른다.

Cursor는 **구조 설계자가 아니라**  
고정된 구조 안에서 **문서를 정확히 구현하는 실행기**이다.

---

## 1️⃣ 절대 불변 원칙 (Violation = 즉시 실패)

### Rule 1 — DB-Only Read
- UI/API는 **engine_snapshot만** 조회
- API 레이어에서 **계산 금지**
- snapshot_data 외부에서 로직 추가 금지
- SELECT는 허용되나, **비즈니스 계산 로직은 금지**
- 위반 시 → 테스트 실패 처리

### Rule 2 — Strict Engine Purity
- **backend/app/engines/**:
  - 순수 함수 **(dict → dict)**
  - **SQLAlchemy import 금지**
  - **Session, text, create_engine 금지**
  - **외부 I/O 금지**
  - **datetime.now 직접 호출 금지** (입력으로 받기)
- 엔진은 **결정 함수**이지 오케스트레이터가 아니다.

### Rule 3 — Single Write Path
- **engine_snapshot**에 대한 INSERT는:
  - **오직 core/snapshot_repo.py에서만** 허용
- 다른 파일에서:
  - `INSERT INTO engine_snapshot`
  - `db.execute(text(...engine_snapshot...))`
  - 발견 시 → **빌드 실패**

### Rule 4 — Safety Priority (코드 레벨 if-guard 고정)
모든 실행 루프는 아래 우선순위를 **명시적 코드**로 준수한다:
- **Emergency Stop** > **Retract** > **Operation Mode**(Backtest/Paper/Pilot/Live) > **Trading Logic**

### Rule 5 — 표시 데이터 메타
모든 표시 데이터는 **source(실명), timestamp(UTC·로컬), refresh_rate 메타**를 포함해야 한다.

---

## 2️⃣ 테스트 우선 개발 (Test = Spec)

### A. Phase 0~1 Acceptance Lock
다음 테스트는 **삭제·수정 금지**:
- Worker 1-cycle → **6종 snapshot_key** 생성
  - engine_heartbeat
  - health_status
  - regime_current
  - allocation_matrix
  - fleet_budget_snapshot
  - portfolio_state
- freshness 정상 동작
- incident_log 폭증 없음
- **테스트 먼저 작성 후 구현.**

### B. Regime Engine Mathematical Lock (SE-39)
다음 항목은 **"정확히 일치"**해야 한다:
- **RegimeScore** = 0.35×PS + 0.25×VS + 0.25×LM + 0.15×SN
- **분류 경계**:
  - ≥ 1.0 → Goldilocks
  - 0 ~ 1.0 → Sideways
  - -1.0 ~ 0 → Tapering
  - ≤ -1.0 → Crisis
- 60MA > 120MA 조건은 TrendScore에 반영
- **CrisisProb** = Logistic(...)
- **3연속 동일 방향**일 때만 Regime 확정

### 🔐 Weight Drift Guard
아래 값 **변경 시 테스트 실패**:
- 0.35, 0.25, 0.25, 0.15
- 1.0, -1.0
- 0.8 (CrisisProb Gate)
- -0.10 (DD), -0.03 (Daily)
- 120 (Freshness sec)

가중치·임계값은 **상수 파일에 고정**하고, 테스트에서 **직접 검증**한다.

---

## 3️⃣ Pre-Trade Gate Hard Lock (SE-50)

Gate는 반드시:
- **Mode Gate**
- **Freshness Gate**
- **Risk Gate**

- **Freshness Gate**는 engine_snapshot 기반만 허용.
- **Risk Gate** 조건:
  - CrisisProb > 0.8 → FAIL
  - DD < -10% → FAIL
  - Daily Loss < -3% → FAIL
- **Gate 로직 우회 금지.**

---

## 4️⃣ Refactor Protection

다음 **변경은 금지**:
- 가중치 변경
- 임계값 변경
- snapshot_key 이름 변경
- Gate 순서 변경
- Regime 분류 경계 수정
- 3연속 안정성 필터 제거
- dict → object 변경 (엔진 출력 타입 변경 금지)

리팩터링은 **"동일 동작 보장 테스트 통과"** 조건에서만 허용.

---

## 5️⃣ Snapshot Contract Lock

**regime_current** snapshot_data는 반드시 포함:
- price_score
- vol_score
- macro_score
- sentiment_score
- regime_score
- regime_state
- crisis_probability
- confidence
- timestamp_utc

**키 제거/이름 변경 금지.**

---

## 6️⃣ 문서 미기재 기능 처리

SE-39/50/64에 **명시되지 않은** 로직은:
- **즉시 구현 금지**
- **TODO 표시**
- **승인 요청**

예:
- RS 상위 20%
- 산업 Bias 필터
- MA slope 조건
- 자본 자동 확장 공식 변경

---

## 7️⃣ 자동 위반 감지 전략 (강력 권고)

다음 테스트를 **추가하라**:
- engines 폴더에서 **sqlalchemy import** 탐지 → FAIL
- engines 폴더에서 **Session 사용** 탐지 → FAIL
- **snapshot_repo 외부**에서 **engine_snapshot** 문자열 탐지 → FAIL
- **RegimeScore 계산식**이 상수 정의와 불일치 시 FAIL

---

## 8️⃣ 개발 모드 원칙

**Cursor는:**
- 구조를 바꾸지 않는다
- 알고리즘을 재해석하지 않는다
- 가중치를 개선하지 않는다
- "더 나은 방법"을 제안하지 않는다

**Cursor의 역할은:**
- **SE Documentation을 코드로 정확히 복제하는 것**

---

## 9️⃣ 실패 기준

다음 중 **하나라도** 발생하면 구현은 **실패**다:
- 테스트 수정으로 통과시킴
- 상수 변경 후 문서 근거 없음
- Gate 우회
- Snapshot 없이 직접 계산
- 엔진이 DB 접근

---

## 🔟 최종 목표

Aegis-X는:

**Snapshot → Gate → Execution**

의 **단방향 구조**를 가진 시스템이다.

**구조는 신성불가침이다.**

---

## 📋 SOP 및 운영문

- **1페이지 SOO (Phase 0-1)**: `docs/Cursor_SOO_Phase0_1.md` — Cursor에 붙여넣어 작업 지시용. 명령·검증·산출물·DO NOT.
- **Guardrails**: `docs/Cursor_Guardrails_SE_Enforcement.md` — 3원칙 테스트 강제, Snapshot Key SSOT, 전략→파라미터, LLM 격리.
- **전략→파라미터 매핑**: `docs/전략_파라미터_매핑_규격.md` — 전략 서술 ↔ 엔진 입력 dict/조건식 잠금.
- **SOP (일반)**: `docs/Cursor_SOP_Standard_Operating_Order.md` — Cursor Chat 시작 시 붙여넣기용.
- **LLM 스태핑/폴백**: `docs/LLM_Staffing_Fallback_Plan.md` — N+1 Fallback, LKS, Warroom 표시 규격.
- **루트 규칙**: `.cursorrules` — 매 세션 상시 적용되는 5개 Non-negotiable Rules.
