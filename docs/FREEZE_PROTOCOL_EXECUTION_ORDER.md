# V3 Architectural Freeze — 실행 순서 및 검증

**SE-39/50/64/65 기준 구조적 정합성.** 확장(US Market ICD, 신규 전략) 전 아키텍처 고정.

---

## PHASE 1 — Gate Priority Hard Lock ✅

- **선형 게이트 체인** (병렬 아님):  
  `EmergencyStop → Retract → LLMBlackout → Mode → Risk → Freshness → Pre-Trade → Strategy`
- **구현**: `backend/app/gates/gate_chain.run_gate_chain(db)`
- **상태**: `system_config` — `gate_emergency_stop_active`, `gate_retract_active`, `llm_blackout_active`
- **테스트**: `backend/tests/test_gate_chain.py` — EmergencyStop 시 전부 차단, Retract 시 차단, Risk 위반 시 차단

---

## PHASE 2 — MetaScore Formalization ✅

- **수식**: `MetaScore = a*Sharpe + b*Expectancy - c*MaxDrawdown`
- **계수**: `system_config.metascore_params` (a, b, c, version)
- **구현**: `backend/app/core/metascore.py` — `get_metascore_params(db)`, `compute_metascore(...)`, `compute_metascore_from_db(db, ...)`

---

## PHASE 3 — Immutable Hash Chain ✅

- **대상**: `engine_snapshot`, `order_log` (컬럼: `prev_hash`, `self_hash`)
- **수식**: `current_hash = SHA256(previous_hash + snapshot_data_json + timestamp)`
- **쓰기**: `snapshot_repo.insert_snapshot_sync`, `order_repo.insert_order_sync` (마이그레이션 003 적용 시)
- **검증**: `scripts/verify_hash_chain.py`, `backend/app/core/hash_chain_verify.py`
- **테스트**: `backend/tests/test_hash_chain.py`

---

## PHASE 4 — LLM Blackout Simulation ✅

- **동작**: 전 Provider 실패 시 `on_blackout(db)` → `incident_log` + `llm_blackout_active` 설정 → Execution Freeze
- **Freeze**: `block_new_orders = True`, `allow_only_risk_reduction = True` (게이트 체인에서 LLMBlackout 단계 차단)
- **테스트**: `backend/tests/test_llm_blackout.py` — Blackout 시 incident 기록, gate chain 차단

---

## PHASE 5 — Snapshot Integrity Check ✅

- **필수 키**: regime_current, allocation_matrix, fleet_budget_snapshot, risk_guard, llm_status, operation_mode, engine_heartbeat
- **스크립트**: `scripts/snapshot_integrity_check.py`
- **모듈**: `backend/app/core/snapshot_integrity.check_snapshot_integrity(db)`
- **테스트**: `backend/tests/test_snapshot_integrity.py`

---

## Absolute Rules (DO NOT BREAK)

- `engines/` — pure dict→dict only
- `engine_snapshot` 쓰기 — `snapshot_repo` only
- API — 전략/엔진 계산 금지, DB 읽기만
- 모든 상태 — DB 기반
- **PowerShell only** (Bash 지시 없음)

---

## Success Condition

- Gate chain 우선순위 테스트 통과
- Hash chain 검증 스크립트 통과 (마이그레이션 003 적용 환경)
- Blackout 시 Freeze + incident 로깅 테스트 통과
- MetaScore 계수 DB 저장·재계산 일치
- Snapshot 무결성 검사 통과 (1사이클 후 필수 키 존재)

이후에만 확장(US Market ICD, 신규 전략) 검토.
