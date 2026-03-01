# 27_CIC_RealTime_Update_Contract.md
목적
Low Latency 구현
방식
SSE 또는 WebSocket
push는 “snapshot_key 변경 이벤트”만 전송
실제 데이터는 DB 재조회
목표
Snapshot 조회 < 200ms
UI 반응 < 500ms