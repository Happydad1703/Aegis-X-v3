# LLM 지능 배분 및 결심 보장 스태핑 플랜 (N+1 Fallback)

**원칙**: Specialization + N+1, 최종적으로 규칙기반(로컬)로 생존 보장.  
**핵심**: 어떤 경우에도 “결정이 안 나서 멈춤”이 아니라, 보수적 모드 전환 / 신규 진입 차단 / 리스크 축소·청산 / DB 기록으로 반드시 다음 행동을 수행한다.

---

## 4-A. 조직/보직별 모델 배치 (Primary / Secondary / Tertiary)

| 조직/보직 | Primary | Secondary | Tertiary | 임무(요약) |
|-----------|---------|-----------|----------|-------------|
| **JCS(합참/CIC)** | 고추론 모델 | 대체 고추론 모델 | 로컬 규칙/룰엔진 | Regime/위기판단, 모드전환, E-Stop/Retract 결심 |
| **STRATCOM(전략)** | 장문맥/분석 모델 | 대체 장문맥 모델 | 로컬 규칙 | 산업 Bias/테마/장기 가드레일 |
| **SRC(자원/리스크)** | 계산/정책 모델 | 대체 | 로컬 Safe Matrix | 자원배분, 노출량, 한도/레버리지 규율 |
| **Core Force(중장기)** | 펀더멘털/구조추세 모델 | 대체 | 룰기반 | 저회전 복리/추세 유지, 승격 규칙 |
| **Swing Force** | 패턴/수급 모델 | 대체 | 룰기반 | 중단기 타점/후퇴/익절 규칙 |
| **Strike Force** | 초단기/민첩 모델 | 대체 경량 | 룰기반 즉시청산 | 지연=손실 → 보수적 즉시정리 |
| **Reserve(예비전단)** | 로컬 룰엔진 | 경량 요약 모델 | N/A | 블랙아웃/통신장애 시 동결·청산·보고 |

※ 실제 모델명은 공급자별 최신으로 바뀔 수 있으므로, **코드에 모델명을 박지 말고** provider/model을 **설정 테이블**로 관리한다.

---

## 4-B. Fallback 로직 (Degradation Ladder)

| Level | 상태 | 동작 |
|-------|------|------|
| **0 (Normal)** | Primary 사용 | 정상 |
| **1 (Degraded)** | Primary 타임아웃/에러 | → Secondary 즉시 재시도 |
| **2 (Conservative)** | Secondary도 불안정 | → Tertiary(경량) + 보수적 ROE |
| **3 (Freeze)** | LLM 전체 장애/데이터 소스 결함 | → 신규 진입 금지, 리스크 축소 |
| **4 (Blackout Survival)** | “암전” | → Last-Known Strategy 유지, 필요 시 규칙기반 청산, 상태 DB 기록 |

---

## 4-C. 구현 지침 — `intelligence/llm_gateway.py` (또는 동등 모듈) 계약

다음 4가지를 반드시 구현한다.

### 1. Multi-Provider Request Spec

- **입력**: `{ task_type, payload, required_quality, max_latency_ms, providers=[...], models=[...] }`
- **출력**: `{ ok, provider_used, model_used, latency_ms, result, error }`

### 2. Health Check Routine

- **주기**: 5분(또는 더 짧게)
- **지표**: 성공률, p95 latency, 최근 n회 타임아웃, 에러코드
- **결과**: “사용가능 모델 리스트”를 **DB에 스냅샷/설정으로 기록**

### 3. Circuit Breaker

- 연속 실패/지연 임계치 초과 시 해당 provider/model **자동 제외(쿨다운)**

### 4. Last-Known Strategy (LKS)

- 마지막 정상 전략/ROE/모드/포트 한도 등을 **DB에 저장**
- 블랙아웃 시 **LKS로 Freeze/Reduce/Exit 수행**

---

## 4-D. Warroom/CIC 표시 규격 (데이터 메타 강제)

모든 위젯(헤더/푸터/본문 포함)은 **최소 다음을 표준 표기**한다:

| 필드 | 설명 |
|------|------|
| `source_name` | 실명 |
| `generated_at` | UTC + local_time(선택) |
| `refresh_rate_sec` | 갱신 주기(초) |
| `freshness_status` | GREEN / YELLOW / RED |
| `operation_mode` | Backtest / Paper / Pilot / Live |
| `llm_status` / `api_engine_status` | LLM·API 엔진 상태 |

---

---

## 최소 구현 요구사항 (끊기지 않게 구현하는 4가지)

Mesh/N+1 Fallback을 실제 운영에서 안 죽게 만들려면, **코드 레벨**로 아래 4개가 필요하다.

| # | 요구사항 | 내용 |
|---|----------|------|
| 1 | **llm_gateway: role 기반 라우팅** | JCS / STRATCOM / SRC / Strike / Reserve 등 **역할별** Primary→Secondary→Tertiary 라우팅 |
| 2 | **health table / snapshot** | `llm_status`는 단순 상태표가 아니라 **provider별** latency, error_rate, last_ok_at 등을 기록 |
| 3 | **degradation ladder** | 장애 시 “다음 모델로 갈아탄다”에서 끝나지 않고, 최종적으로 **LKS + Execution Freeze(또는 Retract)**로 안전 종료까지 구현 |
| 4 | **DB 로깅 의무화** | LLM 호출 성공/실패, fallback 발생, blackout 진입은 **incident_log / command_log**에 남김 → Warroom에서 “왜 그렇게 됐는지” 추적 가능 |

---

*Ref: SOP — Phase 4 LLM Gateway. Safety: EmergencyStop > Retract > Mode > Strategy.*
