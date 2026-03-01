61_Pilot_Ramp_System_Integration_Spec.md

이제 **Pilot Ramp를 시스템에 “구조적으로 봉인”**합니다.
단순 운영 규칙이 아니라:
DB에 기록되고
Gate에 강제되며
UI에 표시되고
Audit 로그가 남는 구조
로 만듭니다.

1️⃣ system_config 테이블 추가
Pilot 단계·Cap·Strike 활성 여부 등을 DB에서 관리합니다.
CREATE TABLE system_config (
    id BIGSERIAL PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL,
    config_value JSONB NOT NULL,
    updated_by VARCHAR(100),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_system_config_key
ON system_config(config_key);
________________________________________
1.1 초기 데이터 삽입
INSERT INTO system_config (config_key, config_value, updated_by)
VALUES (
    'pilot_config',
    '{
        "pilot_step": "P1",
        "pilot_cap_pct": 0.01,
        "strike_enabled": false,
        "daily_entry_limit": 1
    }',
    'SYSTEM_INIT'
);
________________________________________
2️⃣ Config Service
services/config_service.py
from sqlalchemy import text
import json

def get_config(db, key: str):
    q = text("""
        SELECT config_value
        FROM system_config
        WHERE config_key = :k
        ORDER BY updated_at DESC
        LIMIT 1
    """)
    row = db.execute(q, {"k": key}).fetchone()
    return row[0] if row else None


def set_config(db, key: str, value: dict, user: str):
    q = text("""
        INSERT INTO system_config (config_key, config_value, updated_by)
        VALUES (:k, :v::jsonb, :u)
    """)
    db.execute(q, {
        "k": key,
        "v": json.dumps(value),
        "u": user
    })
    db.commit()
________________________________________
3️⃣ Pre-Trade Gate에 Pilot Cap 강제
3.1 cap_gate.py
def cap_gate(order_proposal, portfolio_state, pilot_config):
    cap_pct = pilot_config["pilot_cap_pct"]

    total_equity = portfolio_state["total_equity"]
    max_allowed = total_equity * cap_pct

    order_value = order_proposal["quantity"] * order_proposal["price"]

    if order_value > max_allowed:
        return False, f"Order exceeds pilot cap {cap_pct*100}%"

    return True, "OK"
________________________________________
3.2 pre_trade_gate.py 수정
from app.services.config_service import get_config
from app.gates.cap_gate import cap_gate

pilot_config = get_config(db, "pilot_config")

ok, msg = cap_gate(order_proposal, portfolio_snapshot, pilot_config)
gates.append(("CAP", ok, msg))
if not ok:
    return False, gates
________________________________________
4️⃣ Pilot Step API
routers/control.py 확장
@router.post("/pilot_step")
def change_pilot_step(step: str, user: str):
    valid_steps = {
        "P1": {"pilot_cap_pct": 0.01, "strike_enabled": False, "daily_entry_limit": 1},
        "P2": {"pilot_cap_pct": 0.05, "strike_enabled": False, "daily_entry_limit": 2},
        "P3": {"pilot_cap_pct": 0.10, "strike_enabled": True,  "daily_entry_limit": 3},
        "P4": {"pilot_cap_pct": 0.20, "strike_enabled": True,  "daily_entry_limit": 5},
    }

    if step not in valid_steps:
        return {"error": "Invalid step"}

    config = valid_steps[step]
    config["pilot_step"] = step

    set_config(db, "pilot_config", config, user)

    return {"status": "UPDATED", "step": step}
________________________________________
5️⃣ Strike 활성 여부 반영
engine_worker에서:
pilot_config = get_config(db, "pilot_config")

if not pilot_config["strike_enabled"]:
    fleet_budget["weights"]["STRIKE"] = 0
________________________________________
6️⃣ Daily Entry Limit Gate
추가 Gate:
def daily_entry_gate(db, pilot_config):
    limit = pilot_config["daily_entry_limit"]

    q = text("""
        SELECT COUNT(*)
        FROM order_log
        WHERE created_at::date = CURRENT_DATE
    """)
    count = db.execute(q).scalar()

    if count >= limit:
        return False, "Daily entry limit reached"

    return True, "OK"
Pre-Trade Gate에 포함.
________________________________________
7️⃣ Warroom Header에 표시
Header 추가 항목:
•	Pilot Step: P1
•	Cap: 1%
•	Strike Enabled: No
•	Daily Entry Used: 0/1
모두 snapshot으로 생성:
snapshot_key = pilot_status
________________________________________
8️⃣ Audit Trail
Pilot Step 변경 시:
•	command_log 기록
•	incident_log (INFO) 기록
•	timestamp 포함
________________________________________
9️⃣ 승격 조건 자동 확인 Snapshot
snapshot_key = pilot_progress
{
  "filled_trades": 7,
  "required_for_next": 10,
  "incident_last_7d": 0,
  "dd_violation": false,
  "eligible_for_upgrade": false
}
________________________________________
🔥 현재 상태
이제 Pilot Ramp는:
✔ DB 기반
✔ Gate 강제
✔ UI 표시
✔ Audit 기록
✔ Strike 자동 통제
✔ Cap 자동 통제
상태입니다.
________________________________________
 
