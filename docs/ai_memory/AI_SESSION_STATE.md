# AI Session State (AEGIS-X v3)

## 1) Project identity
- Project: AEGIS-X v3 (DB-First, snapshot read-only UI/API, safety-first operations)
- Environments: Windows 11 + PowerShell workflow, Office PC / Home PC dual-machine development

## 2) Current phase
- Phase: Warroom operations integrity hardening + Office/Home AI context portability lock

## 3) Completed milestones
- Warroom incident operational integrity tests added (`backend/tests/test_warroom_ops_integrity.py`)
- Incident trigger keys/writers/queryability checks added
- Emergency command availability checks added
- Runbook presence guard added (`WARROOM_INCIDENT_CHECKLIST.md`)
- Office/Home AI portability docs added (`AI_CONTEXT_INDEX.md`, `OFFICE_HOME_HANDOFF_PROTOCOL.md`)
- Cursor mandatory first-read context updated in `.cursorrules`
- Context-file presence drift guard added to `test_warroom_ops_integrity.py`

## 4) Current frozen contracts
- UI/API snapshot read-only contract (`engine_snapshot` as source of truth)
- Single write path contract (approved repo/service modules only)
- Gate contract (`failed_gate` must remain in gate order semantics)
- Warroom incident checklist as operational contract baseline

## 5) Current architecture flow
- Ingest -> Engine -> Snapshot publish -> Gate chain -> Execution service -> Order log -> Snapshot/API read
- Warroom frontend reads API snapshot endpoints; no direct compute/data-source bypass

## 6) Current top priorities
- Preserve contract safety before feature speed
- Keep test determinism and avoid hidden state leakage in gate/execution tests
- Maintain operator runbook and incident-response continuity

## 7) Explicit do-not-break items
- Do not add direct `order_log`/`ext_event_raw` reads under `backend/app/api/*`
- Do not introduce ad-hoc write paths outside approved modules
- Do not bypass/reorder emergency and retract precedence without explicit approval
- Do not break snapshot metadata contract (source/timestamp/refresh)

## 8) Last session notes
- Warroom ops integrity tests were introduced and stabilized
- Gate-dependent tests were hardened by explicit test preconditions to reduce flakiness
- Verification baseline (`pytest backend/tests`) reached pass state in agent run
- Office/Home handoff and AI context restore flow documented for cross-machine continuity

## 9) Next recommended task
- Before each machine handoff: update this file, run backend validation, then commit/push

## 10) Required documents to read first
1. `.cursorrules`
2. `docs/ai_memory/AI_CONTEXT_INDEX.md`
3. `docs/ai_memory/AI_SESSION_STATE.md`
4. `docs/ai_memory/CANONICAL_CONTRACT_FREEZE.md`
5. `docs/ai_memory/WARROOM_INCIDENT_CHECKLIST.md` (mandatory for incident/operations tasks)
