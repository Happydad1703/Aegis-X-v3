# 뉴스/자료를 소화하는 엔진 목록

수집(ingest)된 뉴스·공시·매크로 데이터(`ext_event_raw`)가 **어떤 엔진에서 어떻게 소비되는지** 정리합니다.

---

## 1. 데이터 흐름 요약

```
[뉴스/공시/매크로 소스]  →  ingest_worker  →  ext_event_raw (DB)
                                              ↓
engine_worker가 ext_event_raw 집계/참조  →  regime_engine  →  allocation_engine  →  fleet_budget_engine
                                              ↓                    ↓                        ↓
                                         regime_current    allocation_matrix      fleet_budget_snapshot
                                              ↓                    ↓                        ↓
                                         core_engine (regime + allocation + fleet_budget 소비)
                                              ↓
                                         core_force_state  →  Gate / Execution
```

- **엔진은 모두 pure (dict in → dict out)** 이며, DB/네트워크 접근 없음.
- **engine_worker**만 DB를 읽어 `ext_event_raw` 건수·추가 컨텍스트를 엔진 입력으로 넘김.

---

## 2. 뉴스를 소화하는 엔진 목록

| 순서 | 엔진 | 모듈 | 소비하는 입력 | 출력 스냅샷 키 | 비고 |
|------|------|------|----------------|----------------|------|
| 1 | **Regime Engine** | `engines/regime_engine.py` | `events_count` (ext_event_raw 건수), `trend_score`, `volatility_state`, `universe` | `regime_current` | 뉴스/이벤트 건수가 위기 확률·레짐 라벨에 반영 (수식: p_crisis = min(0.95, 0.1 + 0.01×n_events)) |
| 2 | **Allocation Engine** | `engines/allocation_engine.py` | `regime_current` (regime_label, crisis_probability, trend_score) | `allocation_matrix` | 레짐에 따른 CORE/SWING/STRIKE/RESERVE 가중치 (Kelly·Softmax 수식) |
| 3 | **Fleet Budget Engine** | `engines/fleet_budget_engine.py` | `allocation_matrix` (base_weights 등) | `fleet_budget_snapshot` | 할당 결과를 함대 예산 비율로 변환 |
| 4 | **Core Engine** | `engines/core_engine.py` | `regime_current`, `allocation_matrix`, `fleet_budget_snapshot`, `risk_guard`, `macro_context`, `battlefield_state` | `core_force_state` | 구조적 추세·트레이드 시그널·프로모션 후보 (뉴스는 regime/할당 경로로 간접 반영) |
| 5 | **Swing Engine** | `engines/swing_engine.py` | regime, price, ma20, ma60, volume_ratio, breakout_10d, holding_days | `swing_force_state` | Spec Lock v1.0: BUY/SELL/HOLD, stop -8%, max_holding_days 15 |
| 6 | **Strike Engine** | `engines/strike_engine.py` | regime, price, vol_spike, z_score, holding_days | `strike_force_state` | Spec Lock v1.0: entry/exit, tp +5%, sl -3% |

- **직접 소비**: Regime Engine — `engine_worker`가 `ext_event_raw`의 **COUNT(*)** 를 `events_count`로 넘겨 뉴스/이벤트 양을 레짐 수식에 반영.
- **간접 소비**: Allocation → Fleet Budget → Core — Regime 결과를 이어받아 할당·예산·코어포스 상태를 계산.

---

## 3. ingest 소스 → 엔진 반영

| ingest source_name | event_type | Regime Engine 반영 |
|-------------------|------------|---------------------|
| ingest_worker | heartbeat | ext_event_raw 건수 증가 → events_count ↑ |
| FRED | macro | 동일 (건수) |
| ECOS | macro | 동일 (건수) |
| DART | disclosure | 동일 (건수) |
| Naver | news | 동일 (건수) |
| Yonhap | news | 동일 (건수) |
| Edaily | news | 동일 (건수) |
| Finnhub | quote | 동일 (건수) |
| AlphaVantage | quote | 동일 (건수) |

현재는 **이벤트 건수만** Regime에 사용되며, 추후 `macro_context`/뉴스 본문 등은 Regime 입력 확장으로 반영 가능.

---

## 4. 통신점검 (연동 점검)

| 단계 | 내용 | 스크립트 |
|------|------|----------|
| 1 | 외부 자료원 API 통신 | `python scripts/check_comm.py` |
| 2 | 수집 1회 → ext_event_raw 기록 | `python scripts/run_ingest_cycle.py` |
| 3 | 엔진 1회 실행 (regime → allocation → fleet → core) | `python scripts/run_engine_cycle.py` |
| 4 | 뉴스 소화 엔진 출력 스냅샷 확인 | `run_engine_comm_check.py` 내 자동 조회 |

**한 번에 실행**: `.\scripts\run_engine_comm_check.ps1` 또는 `python scripts/run_engine_comm_check.py`

- **외부 API**: FRED, ECOS, DART, Naver, 연합 RSS, 이데일리 RSS, Finnhub, Alpha Vantage, LLM, KIS.
- **수집 → DB**: `verify_ingest_db.py` 로 ext_event_raw 기록 여부 확인.
- **엔진 연동**: ingest 1회 + engine 1회 후 `regime_current`, `allocation_matrix`, `fleet_budget_snapshot`, `core_force_state` 존재 여부 확인.

위 통신점검을 모두 통과하면 “뉴스 수집 → DB 기록 → 엔진이 해당 데이터를 소화”하는 경로가 정상 동작하는 것으로 간주합니다.
