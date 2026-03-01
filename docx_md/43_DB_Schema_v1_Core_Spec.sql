43_DB_Schema_v1_Core_Spec.sql

아래는 핵심 테이블 구조입니다. (PostgreSQL 15 기준)
1️⃣ 원천 이벤트 테이블
CREATE TABLE ext_event_raw (
    id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_timestamp TIMESTAMPTZ,
    UNIQUE(source_name, event_timestamp)
);

CREATE INDEX idx_ext_event_source_time
ON ext_event_raw(source_name, received_at DESC);
________________________________________
2️⃣ 매크로 컨텍스트
CREATE TABLE macro_context (
    id BIGSERIAL PRIMARY KEY,
    source_name VARCHAR(100),
    indicator_name VARCHAR(100),
    value NUMERIC,
    observed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_macro_indicator_time
ON macro_context(indicator_name, observed_at DESC);
________________________________________
3️⃣ 엔진 결과 (Raw 계산 결과)
CREATE TABLE engine_result (
    id BIGSERIAL PRIMARY KEY,
    engine_name VARCHAR(100),
    result_key VARCHAR(100),
    result_value JSONB,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_engine_name_time
ON engine_result(engine_name, computed_at DESC);
________________________________________
4️⃣ 스냅샷 테이블 (Warroom 전용 SSOT)
CREATE TABLE engine_snapshot (
    id BIGSERIAL PRIMARY KEY,
    snapshot_key VARCHAR(100) NOT NULL,
    snapshot_data JSONB NOT NULL,
    freshness_status VARCHAR(20) DEFAULT 'GREEN',
    source_name VARCHAR(100),
    generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_snapshot_key_time
ON engine_snapshot(snapshot_key, generated_at DESC);
Warroom은 반드시 이 테이블만 조회.
________________________________________
5️⃣ 의사결정 로그
CREATE TABLE decision_log (
    id BIGSERIAL PRIMARY KEY,
    decision_type VARCHAR(100),
    battlefield VARCHAR(50),
    fleet VARCHAR(50),
    decision_data JSONB,
    executed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
________________________________________
6️⃣ 사고/경보 로그
CREATE TABLE incident_log (
    id BIGSERIAL PRIMARY KEY,
    severity VARCHAR(20),
    category VARCHAR(100),
    message TEXT,
    related_snapshot_key VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
________________________________________
7️⃣ 명령 로그 (Control Panel)
CREATE TABLE command_log (
    id BIGSERIAL PRIMARY KEY,
    command_type VARCHAR(100),
    issued_by VARCHAR(100),
    command_payload JSONB,
    status VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
________________________________________
8️⃣ LLM 사용 로그
CREATE TABLE llm_usage_log (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(100),
    prompt_hash VARCHAR(64),
    response_time_ms INT,
    token_usage INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
________________________________________
📘 44_Snapshot_Key_Catalog_v1
Warroom Home에 반드시 필요한 snapshot_key:
snapshot_key	설명
regime_current	현재 Regime 상태
allocation_matrix	Battlefield + Fleet 배분
strike_risk_status	Strike 상태
swing_force_status	Swing 상태
core_force_status	Core 상태
portfolio_variance	종목별 현재 비중
battlefield_status	전장별 상태
health_status	DB/KIS/API 상태
mode_status	현재 운용 모드
incident_summary	최근 10개 경보
________________________________________
📘 45_API_Contract_v1 (FastAPI)
Read Endpoints
GET /api/snapshot/{snapshot_key}
GET /api/snapshot/latest?key=regime_current
GET /api/health
GET /api/mode
응답 형식:
{
  "snapshot_key": "regime_current",
  "data": {...},
  "freshness_status": "GREEN",
  "generated_at": "2026-03-01T12:30:00Z"
}
________________________________________
Control Endpoints
POST /api/control/freeze
POST /api/control/retract
POST /api/control/stop
POST /api/mode/set
모든 POST는:
•	role 확인
•	command_log 기록
•	snapshot 갱신
•	incident 생성 가능
________________________________________
📘 46_Warroom_Home_Component_Tree (React)
<WarroomLayout>
   <HeaderStatusBar />
   <LeftTreeMenu />
   <MainCanvas>
        <GlobalRegimeCard />
        <BattlefieldHeatmap />
        <AllocationMatrixPanel />
        <FleetStatusGrid>
            <StrikePanel />
            <SwingPanel />
            <CorePanel />
            <ReservePanel />
        </FleetStatusGrid>
        <PortfolioVarianceTopN />
        <IncidentFeed />
   </MainCanvas>
   <FooterTicker />
</WarroomLayout>
________________________________________
HeaderStatusBar 표시 항목
•	Mode
•	Regime
•	CrisisProb
•	DB Status
•	KIS Status
•	Snapshot Freshness
•	LLM Status
모든 항목은:
•	source_name
•	timestamp
•	refresh rate
를 함께 표시.
________________________________________
 
