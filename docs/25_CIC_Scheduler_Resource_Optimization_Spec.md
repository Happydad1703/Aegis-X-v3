# 25_CIC_Scheduler_Resource_Optimization_Spec.md
목적
“죽지 않는 시스템” 구현
1. Resource Inputs
CPU
RAM
DB latency
Network error rate
2. Adaptive Scan Multiplier
scan_multiplier 동적 조정
3. Circuit Breaker
연속 실패 N회 시 source isolate
4. Refresh Tier
critical_only
normal
low_resource