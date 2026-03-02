# 24/7 Follow-the-Sun — Minimal Safe Build Spec

## 개요

- **원칙**: 아키텍처/엔진 순수성 변경 없음. DB-Only Read, Engine Pure (dict→dict), Single Write Path, 기존 Gate 순서, KIS 단일 실행 채널 유지.
- **세션**: `get_current_session(now_utc)` → `"KR"` | `"US"` | `"OFF"`. 구간은 `system_config.follow_the_sun_windows`에 저장 (하드코드 금지).

---

## SECTION 1 — Timezone Layer

- **모듈**: `backend/app/core/timezone_service.py`
- **API**:
  - `get_current_session(now_utc, db=None)` → `"KR"` | `"US"` | `"OFF"`
  - `get_session_multiplier(session, db=None)` → `float` (KR=1.0, US=설정값 e.g. 0.7, OFF=0.0)
- **세션 구간 (기본값, config 없을 때)**:
  - KR: 00:00–06:30 UTC
  - US: 13:00–20:00 UTC
  - OFF: 그 외
- **설정 키**: `follow_the_sun_windows`, `follow_the_sun_multipliers` (system_config)

---

## SECTION 2 — Universe Switch

- **모듈**: `backend/app/core/universe_selector.py`
- **API**: `universe_selector(session)` → `korea_universe` | `us_universe` | `empty_universe` (dict)
- **엔진**: allocation/regime/fleet_budget 엔진은 수정하지 않음. Worker가 `universe`를 input dict에 넣어 전달.

---

## SECTION 3 — USD Risk Gate 확장

- **위치**: `backend/app/gates/risk_gate.py` (기존 구조 유지)
- **추가 검사**: `usd_exposure_ratio <= config.usd_limit`, `fx_volatility <= config.fx_vol_cap`
- **설정**: `system_config.usd_risk_limits` → `{ "usd_limit", "fx_vol_cap" }`
- **위반 시**: incident_log 기록 후 게이트 차단 (Level 1/2 alarm)
- **데이터 소스**: `risk_guard` 또는 `usd_exposure_status` 스냅샷

---

## SECTION 4 — Session Behavior (Gate Layer)

- **KR**: 정상 운영
- **US**: `session_multiplier`로 할당 축소 (예: 0.7) — 스냅샷에 반영, 실행 시 적용
- **OFF**: `block_new_orders = True`, `allow_only_risk_reduction = True` (게이트에서 `active_session == "OFF"`일 때 차단)
- **게이트 순서**: 기존 선형 체인 유지. Session 게이트는 LLMBlackout 다음, Mode 이전에 위치.

---

## SECTION 5 — Snapshot 확장 (추가 키만)

- **추가 스냅샷 키**: `active_session`, `session_state`, `timezone`, `usd_exposure_status`
- **기존 스냅샷 구조 변경 없음**. `snapshot_keys.ALLOWED_SNAPSHOT_KEYS` 및 `signal_interface_master.json`에만 추가.

---

## SECTION 6 — Global Capital (2-Level)

- **구조**: `global_capital` → `session_allocation` (session_multiplier 적용) → `fleet_allocation`
- **구현**: `fleet_budget_engine` 변경 없음. `session_state`에 `session_multiplier` 저장.
- **적용**: `core/session_allocation.apply_session_multiplier_to_fleet_budget(fleet_budget_snapshot, session_state_snapshot)` — consumer가 사용 시 배수 적용.

---

## SECTION 7 — 테스트

- **파일**: `backend/tests/test_follow_the_sun.py`
- **내용**: 세션별 universe 변경, 엔진 순수성(no SQL), OFF 세션 시 신규 주문 차단, USD/FX 위반 시 Risk 게이트 차단, 스냅샷 메타데이터 키, 게이트 순서 불변.
- **DB 미준비 시**: `system_config` / `engine_snapshot` 없으면 해당 DB 의존 테스트는 skip.

---

## 절대 규칙 (유지)

- 새 브로커/멀티 계정 로직 금지
- 엔진 알고리즘 수정 금지
- async 대규모 리팩터 금지
- Windows PowerShell 호환 유지
- Freeze 조건 유지
