# 22_CIC_Control_Safety_Spec.md
목적
Freeze / Retract / Emergency Stop / Mode Change 상세 제어 명세
포함
1. Control State Machine
DISARMED
ARMED
EXECUTING
LOCKED
2. Freeze
신규 진입 차단
DB 기록 필수
3. Retract
R1/R2/R3 프로파일
Risk Mode 조정
Strike Disable
4. Emergency Stop
Freeze Only
Freeze + Flatten
2단계 확인
Decision + Incident 기록
5. Control API Contract
POST /api/cic/control
GET /api/cic/control/status