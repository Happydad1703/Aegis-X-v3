49_Mode_Execution_Layer_Spec.md (v1.0)
이제 Mode Execution Layer를 고정합니다.
이 레이어는 Aegis-X에서 가장 중요한 “사고 방지 장치”입니다.
어떤 모드에서 어떤 행동이 허용되는가를 수학적으로 봉인한다.

1️⃣ 목적
Mode는 단순 UI 상태가 아닙니다.
Mode는:
•	주문 생성 허용 여부
•	Risk Gate 강도
•	자본 사용 한도
•	Strike 활성화 여부
•	LLM 영향 범위
를 결정하는 상위 통제 변수입니다.
________________________________________
2️⃣ Mode 정의
Mode	의미	주문	KIS	자본
BACKTEST	과거 데이터 검증	❌	❌	가상
PAPER	현재시장 모의	모의	❌	가상
PILOT	제한 실거래	제한	✅	실
FULL_LIVE	전면 실거래	전면	✅	실
________________________________________
3️⃣ Mode 상태는 반드시 DB에 저장
테이블 추가
CREATE TABLE system_mode (
    id SERIAL PRIMARY KEY,
    mode VARCHAR(20) NOT NULL,
    changed_by VARCHAR(100),
    changed_at TIMESTAMPTZ DEFAULT NOW()
);
현재 모드는 항상:
SELECT mode FROM system_mode ORDER BY changed_at DESC LIMIT 1;
________________________________________
4️⃣ Mode Engine 구현
4.1 mode_service.py
from sqlalchemy import text

VALID_MODES = ["BACKTEST", "PAPER", "PILOT", "FULL_LIVE"]

def get_current_mode(db):
    q = text("""
        SELECT mode
        FROM system_mode
        ORDER BY changed_at DESC
        LIMIT 1
    """)
    row = db.execute(q).fetchone()
    return row[0] if row else "BACKTEST"


def set_mode(db, new_mode: str, changed_by: str):
    if new_mode not in VALID_MODES:
        raise ValueError("Invalid mode")

    q = text("""
        INSERT INTO system_mode (mode, changed_by)
        VALUES (:m, :u)
    """)
    db.execute(q, {"m": new_mode, "u": changed_by})
    db.commit()
________________________________________
5️⃣ Mode Enforcement Matrix
이제 핵심입니다.
모드에 따라 엔진 행동이 달라집니다.
________________________________________
5.1 주문 생성 허용 여부
def is_order_allowed(mode: str) -> bool:
    if mode == "BACKTEST":
        return False
    if mode == "PAPER":
        return True
    if mode == "PILOT":
        return True
    if mode == "FULL_LIVE":
        return True
    return False
________________________________________
5.2 KIS 호출 허용 여부
def is_kis_enabled(mode: str) -> bool:
    return mode in ["PILOT", "FULL_LIVE"]
________________________________________
5.3 Strike 제한 강화
def strike_multiplier(mode: str) -> float:
    if mode == "BACKTEST":
        return 1.0
    if mode == "PAPER":
        return 1.0
    if mode == "PILOT":
        return 0.5
    if mode == "FULL_LIVE":
        return 1.0
Pilot에서는 Strike 50% 축소.
________________________________________
5.4 자본 사용 상한
def capital_cap(mode: str) -> float:
    if mode == "PILOT":
        return 0.2  # 전체 자본의 20%만 사용
    if mode == "FULL_LIVE":
        return 1.0
    return 1.0
________________________________________
6️⃣ Engine Worker에 Mode 적용
engine_worker.py 내:
from app.services.mode_service import get_current_mode

mode = get_current_mode(db)
Strike 계산 이후:
from app.services.mode_service import strike_multiplier, capital_cap

mult = strike_multiplier(mode)
fleet_budget["weights"]["STRIKE"] *= mult

cap = capital_cap(mode)
fleet_budget["capital_cap"] = cap
________________________________________
7️⃣ FULL_LIVE 보호 규칙
FULL_LIVE 진입은 자동 금지.
조건:
•	Pilot 30건 이상
•	DD 위반 없음
•	Incident rate < 2%
API에서:
if new_mode == "FULL_LIVE":
    raise Exception("Manual approval required")
________________________________________
8️⃣ Telegram 제한
메신저에서는:
•	Mode 하향만 가능
•	상향은 Web UI + Confirm + Reason 필수
________________________________________
9️⃣ Warroom Header 표시
Header:
•	MODE: PILOT
•	Capital Cap: 20%
•	Strike Multiplier: 0.5
•	KIS: ENABLED
________________________________________
🔥 지금 상태
이제 Aegis-X는:
•	BACKTEST
•	PAPER
•	PILOT
•	FULL_LIVE
모드별 행동이 구조적으로 분리되었습니다.
실수로 실거래가 나갈 가능성이 크게 줄었습니다.
________________________________________
 
