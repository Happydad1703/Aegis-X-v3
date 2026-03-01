# Aegis-x v3

Design Freeze: SE-01 ~ SE-65 (Architecture Lock)

Key invariants:
- DB-First / UI reads snapshots only
- Mode enforcement: BACKTEST / PAPER / PILOT / FULL_LIVE
- Pilot Ramp: P1~P4 via system_config + Gate enforcement
- Pre-trade multi-gate risk system
- Follow-the-sun session policy
- Capital scaling strategy

