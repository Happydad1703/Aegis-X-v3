# 24_CIC_Data_Transparency_Standard.md
목적
실명제 + Timestamp + Refresh + Freshness 의무화 규칙
모든 데이터에 반드시 포함:
source_name
timestamp_utc
local_time
refresh_interval_sec
freshness_status
confidence
latency_ms
Freshness 계산 로직
1× refresh → GREEN
2× refresh → YELLOW
2× → RED
RED 2개 이상 → Auto Freeze