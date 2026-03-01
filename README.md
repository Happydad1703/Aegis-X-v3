# Aegis-x v3

Design Freeze: SE-01 ~ SE-65 (Architecture Lock)

**Git push:** 로컬에서 초기 커밋까지 완료됨. 원격에 푸시하려면 GitHub(또는 사용 중인 호스트)에서 `Aegis-X_v3` 저장소를 만든 뒤, 원격 URL이 다르면 `git remote set-url origin <본인-저장소-URL>` 로 수정하고 `git push -u origin master` 실행.

Key invariants:
- DB-First / UI reads snapshots only
- Mode enforcement: BACKTEST / PAPER / PILOT / FULL_LIVE
- Pilot Ramp: P1~P4 via system_config + Gate enforcement
- Pre-trade multi-gate risk system
- Follow-the-sun session policy
- Capital scaling strategy

