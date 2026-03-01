# 외부기관 · 모듈 · LLM 프로세스결과 · DB 매칭 테이블 (Aegis-X v3)

**목적**: 뉴스/정보/매크로/공시/브로커/LLM 등 **외부기관** → **처리 모듈** → **LLM 사용(역할)** → **프로세스 결과(산출물)** → **DB 저장 위치**를 1:1로 매칭한다.

**원칙**: DB-First, Single Write Path. 모든 산출은 repo 경유로만 DB 기록.

---

## 1. 외부기관 → 수집 모듈 → DB (원시/이벤트)

| 구분 | 외부기관(표시명) | 처리 모듈 (v3) | LLM 사용 | 프로세스 결과 | DB 테이블 | event_type / source_name (참고) |
|------|------------------|----------------|----------|---------------|-----------|----------------------------------|
| **매크로** | FRED | ingest_worker / fred collector (확장 시) | 없음 | 시계열 원시 데이터 | ext_event_raw, macro_context(확장 시) | FRED_EVENT, source_name=FRED |
| **매크로** | ECOS | ingest_worker / ecos collector (확장 시) | 없음 | 경제통계 원시 데이터 | ext_event_raw, macro_context(확장 시) | ECOS_EVENT, source_name=ECOS |
| **공시** | DART | ingest_worker / dart collector (확장 시) | 없음 | 공시 목록·요약 원시 | ext_event_raw, macro_context(확장 시) | DART_EVENT, source_name=DART |
| **뉴스** | 네이버 뉴스 | ingest_worker (확장 시) | 없음 | 뉴스 검색 결과 원시 | ext_event_raw | NEWS_EVENT, source_name=Naver |
| **뉴스** | Finnhub | ingest_worker (확장 시) | 없음 | 글로벌 뉴스 원시 | ext_event_raw | NEWS_EVENT, source_name=Finnhub |
| **뉴스** | Alpha Vantage | ingest_worker (확장 시) | 없음 | 뉴스 감성 원시 | ext_event_raw | NEWS_EVENT, source_name=AlphaVantage |
| **뉴스** | 다음/Kakao | ingest_worker (확장 시) | 없음 | 웹/뉴스 검색 원시 | ext_event_raw | NEWS_EVENT, source_name=Daum |
| **뉴스** | 연합인포맥스 RSS | ingest_worker (확장 시) | 없음 | RSS 피드 원시 | ext_event_raw | NEWS_EVENT, source_name=YonhapInfomax |
| **뉴스** | 이데일리 RSS | ingest_worker (확장 시) | 없음 | RSS 피드 원시 | ext_event_raw | NEWS_EVENT, source_name=Edaily |
| **브로커** | KIS | execution/kis_executor, 주문·잔고 동기화 | 없음 | 주문·체결·잔고 | order_log, engine_snapshot(portfolio_state 등) | — |
| **인프라** | PostgreSQL | — | — | 모든 테이블 저장소 | ext_event_raw, engine_snapshot, order_log, incident_log, command_log, system_mode, system_config | — |

---

## 2. (원시/스냅샷 입력) → 엔진·LLM → 프로세스 결과 → DB (스냅샷/로그)

| 입력 소스 (DB/이벤트) | 처리 모듈 | LLM 사용 (역할 / Provider) | 프로세스 결과 (산출물) | DB 테이블 | snapshot_key / 비고 |
|----------------------|-----------|---------------------------|------------------------|-----------|----------------------|
| ext_event_raw, macro_context | regime_engine | **JCS** — OpenAI(국면)·Claude/Gemini(보조) | Regime 상태, CrisisProb, Confidence | engine_snapshot | regime_current |
| ext_event_raw (뉴스) | (뉴스 요약/감성) | **JCS·정보작전** — OpenAI/Gemini 뉴스 스캔·요약 | 뉴스 요약·감성 점수 (Regime 입력 보조) | engine_snapshot, ext_event_raw(요약 저장 시) | (예) news_sentiment, regime 입력 |
| regime_current, battlefield | allocation_engine, fleet_budget_engine | 없음 (순수 계산) | 전장 가중치, Fleet 예산 | engine_snapshot | allocation_matrix, fleet_budget_snapshot |
| regime_current, allocation, portfolio | risk_gate, risk_engine | 없음 (또는 SRC 계산/정책 모델) | Risk 통과 여부, Strike 조정 | engine_snapshot | risk_guard |
| regime_current, allocation | **STRATCOM** — Claude/Gemini (산업 Bias/테마) | 장문맥·전략 Bias | 산업 Bias, 테마 가드레일 (확장 시) | engine_snapshot, system_config | (확장 시) strategy_bias |
| allocation, Fleet 타겟 후보 | strike_engine, swing_engine, core_engine | **Strike** — DeepSeek(경량) / **Swing·Core** — 룰 또는 LLM | 후보군·선정 타겟, ROE 적용 | engine_snapshot, engine_result | strike_targets, swing_targets, core_targets 등 |
| 주문 요청 | pre_trade_gate, execution | 없음 | Gate 통과 → 주문 실행 | order_log | — |
| order_log, 포지션 종료 | trade_lifecycle / AAR 엔진 | **J-4 사후강평** — Gemini(선택) AAR·교훈 추출 | Battle Report, AAR 점수 | battle_report, engine_snapshot | battle_report |
| AAR·전략 성과 | Meta-Control, AAR Learning | 없음 (또는 전략 요약 LLM) | 전략 State, 파라미터 Bounded 조정 | system_config, engine_snapshot | operation_mode, (튜닝 반영 스냅샷) |
| (헬스 체크) | engine_worker, comm check | 없음 | 엔진 생존, LLM/API 가용성 | engine_snapshot | engine_heartbeat, comm_health, llm_status |

---

## 3. LLM별 역할 → 산출물 → DB 요약

| LLM (Provider) | 담당 역할 (R&R) | 주요 산출물 | DB 저장 위치 |
|----------------|-----------------|-------------|--------------|
| **OpenAI** | JCS(국면)·Regime·고추론, 리밸런싱·뉴스 스캔 | regime_current, 뉴스 요약, 리밸런싱 제안 | engine_snapshot (regime_current 등) |
| **Anthropic (Claude)** | STRATCOM 전략·장문맥, JCS 보조 | 산업 Bias, 전략 가드레일, 시황 리포트 | engine_snapshot, system_config |
| **Gemini** | 참모·뉴스 요약, J-4 사후강평(AAR) | 뉴스 요약, AAR·교훈 요약 | engine_snapshot, battle_report 연계 |
| **DeepSeek** | Strike 등 경량·비용 효율 | 타겟 선정, 전술 제안 | engine_snapshot (strike_targets 등) |
| **(로컬 룰)** | SRC, Reserve, Tertiary Fallback | 자원 한도, 동결·청산 결정 | engine_snapshot (risk_guard, operation_mode) |

---

## 4. DB 테이블별 수집·산출 요약

| DB 테이블 | 수집/산출 소스 | 처리 모듈 | 비고 |
|-----------|----------------|-----------|------|
| **ext_event_raw** | FRED, ECOS, DART, 네이버, Finnhub, Alpha Vantage, Kakao, 연합인포맥스, 이데일리 | ingest_worker (확장 시) | event_type, source_name 구분 저장 |
| **macro_context** | FRED, ECOS, DART (확장 시) | ingest_worker / collectors | 마이그레이션 확장 시 |
| **engine_snapshot** | 엔진·워커·LLM 산출 전부 | engine_worker, snapshot_repo | Single Write Path: snapshot_repo 경유만 |
| **order_log** | KIS 주문·체결 | execution/kis_executor, paper_executor | 51_Order_Execution |
| **battle_report** | 포지션 종료, AAR 엔진 | trade_lifecycle, AAR 모듈 | 53_AAR, 40_AAR_Learning |
| **incident_log** | Gate 실패, 엔진 오류, 위험 임계치 | incident_repo, gates, workers | 감사·알림 |
| **command_log** | Freeze/Retract/Stop, 모드 변경 | command_repo, api/control | 감사 |
| **system_mode** | 모드 전환 | mode_service, api/control | BACKTEST/PAPER/PILOT/LIVE |
| **system_config** | ROE, 전략 프로필, 튜닝 파라미터 | config_service, Meta-Control | 09_Meta_Control |

---

## 5. Snapshot Key ↔ 외부기관·모듈·LLM 요약

| snapshot_key | 주 입력 | 처리 모듈 | LLM | 비고 |
|--------------|---------|-----------|-----|------|
| engine_heartbeat | — | engine_worker | 없음 | 엔진 생존 |
| comm_health | 외부 API 통신 상태 | engine_worker / comm check | 없음 | FRED/KIS 등 통신 상태 |
| regime_current | ext_event_raw, macro_context | regime_engine | JCS (OpenAI/Claude/Gemini) | 국면·CrisisProb |
| operation_mode | system_mode, command | mode_service | 없음 | Backtest/Paper/Pilot/Live |
| llm_status | LLM Health Check | llm_gateway (Phase 4) | — | 가용 Provider/모델 |
| risk_guard | regime, portfolio, allocation | risk_gate, risk_engine | 없음 (또는 SRC) | Gate·Strike 조정 |
| allocation_matrix | regime_current, battlefield | allocation_engine | 없음 | 전장 가중치 |
| fleet_budget_snapshot | allocation, growth | fleet_budget_engine, capital_scaling | 없음 | Strike/Swing/Core/Reserve |
| (확장) portfolio_state | order_log, KIS 잔고 | execution, portfolio 집계 | 없음 | 포지션·평가 |
| (확장) battle_report | order_log, 종료 감지 | AAR 엔진 | J-4 Gemini(선택) | 전투 결과·AAR 요약 |

---

## 6. 참조 문서

- **입력 DB → 프로세싱 → 출력 DB · Dashboard**: `docs/입력DB_프로세싱_출력DB_대시보드_매칭테이블.md`
- **외부기관 목록·저장소**: `docs/외부기관_목록_및_통신점검.md`
- **프로세스·모듈·Warroom**: `docs/SE_Process_Module_DB_Warroom_Mapping_Table.md`
- **LLM R&R·점검**: `docs/합참_SRC_각군_LLM_RR_점검_결과.md`, `docs/LLM_Staffing_Fallback_Plan.md`
- **ICD·DDD**: `docs/03_External_Interface_Control_Document_ICD.md`, `docs/04_Data_Architecture_DDD.md`
