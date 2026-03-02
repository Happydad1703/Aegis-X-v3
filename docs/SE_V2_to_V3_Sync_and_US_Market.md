# SE 문서 동기화: V2 → V3 및 미국 시장 반영

**목적**: V2의 성공적인 SE(시스템 공학) 표준을 V3에 이식하고, 미국 시장(US Market) 특수성을 반영한다.  
**기준**: AegisX_SE_Documentation_Sets_v1.0, CTO 관점 Cross-Project Knowledge Transfer.

---

## 1. V2 참조 SE 문서 (17종 대응)

V2 `docs/` 및 `system/docs/SE/` 기준 핵심 문서와 V3 대응·동기화 상태.

| # | V2 문서 (참조) | V3 위치·비고 |
|---|----------------|--------------|
| 1 | SE_Engineering_Documentation.md (Phase 1~6) | docs/ 구현 로드맵·Phase0_1_Run_Checklist, SE_64/65 |
| 2 | 10_Self_Healing_Spec.md | docs/ (동일 번호 유지). Self-Healing·Emergency Mode |
| 3 | 11_Governance_Audit_Spec.md | docs/11_Governance_Audit_Spec.md — **Hash Chain** 구현: audit_chain.py, §4.2 레코드 형식 명시 |
| 4 | ZERO_FLASH_SPEC.md | docs/ZERO_FLASH_SPEC.md 이식 완료. Warroom critical CSS·30초 주기 적용 |
| 5 | DESIGN_PRINCIPLE_DB_FIRST.md | V3 DB-First 원칙 (README, 계약 테스트) |
| 6 | FLEET_SITUATION_STRATEGY, FLEET_TARGET_SELECTION | V3 engines (core_engine, allocation, regime), SE_08·SE_06 |
| 7 | JCS_Integrated_Master_Plan_And_Schedule | V3 모듈 구조·Phase0-1 완성 기준 |
| 8 | TRACEABILITY_GOVERNANCE, LEDGER_INTEGRITY_POLICY | 11_Governance + audit_chain |
| 9 | DATA_FLOW_AND_SSOT | snapshot_keys, snapshot_repo, engine_snapshot SSOT |
| 10 | 03_External_Interface_Control_Document_ICD | docs/03_External_Interface_Control_Document_ICD.md — **§3 US Market** 추가 (T+2, DST, Yahoo/Polygon/Alpha Vantage) |
| 11 | Regime/Allocation 로직 (regime_definer, resource_manager) | V3 regime_engine (수식 Locking), allocation_engine (Kelly·Softmax 수식) |
| 12 | REFRESH_AND_RESOURCE_SCHEDULING | 30초 이상 주기, ZERO_FLASH_SPEC |
| 13 | CIC_대시보드_시험평가, Warroom_CIC | Warroom index.html, /api/snapshot, /api/control |
| 14 | ENV_WINDOWS_REFERENCE, Config | docs/ENV_Windows11_API_Keys.md, 16_Config_Management_Plan |
| 15 | OPERATIONS_MANUAL, RUN | docs/System_Operations_Manual.md, Phase0_1_Run_Checklist |
| 16 | REBALANCING_ENGINE_DESIGN | allocation_engine, fleet_budget_engine |
| 17 | Audit/Incident (audit_chain, incident_log) | audit_chain.py, incident_repo, command_repo |

---

## 2. 미국 시장(US Market) 반영 요약

| 항목 | 내용 |
|------|------|
| **결제일** | T+2 (Settlement). 캘린더·주문 로직에서 영업일 기준 +2일 반영 |
| **서머타임(DST)** | ET: 3월 둘째 일요일~11월 첫 일요일 EDT(UTC-4), 그 외 EST(UTC-5). 타임스탬프는 저장·계산 모두 UTC, 표시만 ET 변환 |
| **데이터 소스** | Yahoo Finance (RapidAPI), Polygon.io, Alpha Vantage — ICD §3.2 테이블 및 Failure Handling §3.3 |
| **환경변수** | RAPIDAPI_KEY, POLYGON_API_KEY, ALPHA_VANTAGE_API_KEY, FRED_API_KEY (기존) |
| **모듈** | ingest_worker 확장 시 source_name=Yahoo|Polygon|AlphaVantage; check_comm 확장 시 해당 키 점검 |

---

## 3. 로직 이식·강화 (V3 방침)

- **Regime**: 핵심 계산은 Python 수식(regime_engine.compute_regime). LLM은 '최종 판정 및 해설'로 한정(선택 적용).
- **Allocation**: Kelly Criterion·Softmax 벡터 연산으로 Locking (allocation_engine.py). numpy 활용.
- **Governance**: Hash Chain Logging 필수 — audit_chain.append_audit_event, 11_Governance §4.2 레코드 형식 준수.

---

## 4. UI/UX 안정화 (Dashboard Flashing 방지)

- **Zero-Flash**: location.reload() 금지, fetch/WebSocket/SSE만 사용. Warroom: critical CSS 인라인, 30초 주기.
- **향후 SPA**: Layout memo, 필드별 구독, 고빈도 데이터는 전용 Context/스트림.

---

## 5. 검증 체크리스트

- [ ] Hash Chain: regime/allocation/emergency_stop 발생 시 ssot/audit_chain.jsonl에 prev_hash/self_hash 기록
- [ ] 03_ICD §3 US Market 반영 확인
- [ ] ZERO_FLASH_SPEC: Warroom index.html에 zero-flash-critical 스타일, theme-color, 30초 주기
- [ ] Allocation: softmax/kelly_fraction 수식 사용, formula 필드 산출물 포함

---

*문서 버전: v1.0 | V2→V3 Cross-Project Knowledge Transfer*
