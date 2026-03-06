# Office/Home Handoff Protocol (AEGIS-X v3)

## A) Before leaving Office PC
1. Update `docs/ai_memory/AI_SESSION_STATE.md`:
   - what was completed
   - what is next
   - known risks/incidents
2. Run `git status --short` and verify intended changes only
3. Run backend validation:
   - `python -m pytest backend/tests -q -W error::sqlalchemy.exc.SAWarning`
4. Commit with clear message and push to remote branch
5. Ensure no unstated assumptions remain (write them into `AI_SESSION_STATE.md`)

## B) After opening Home PC
1. `git pull`
2. Open Cursor in repository root
3. Read in order:
   - `.cursorrules`
   - `docs/ai_memory/AI_CONTEXT_INDEX.md`
   - `docs/ai_memory/AI_SESSION_STATE.md`
4. If task is incident/operations-related, also read:
   - `docs/ai_memory/WARROOM_INCIDENT_CHECKLIST.md`
5. Ask Cursor to summarize current phase, frozen contracts, and next task before coding

## C) Recovery check (must pass before coding)
- Confirm current phase matches `AI_SESSION_STATE.md`
- Confirm frozen contracts from `CANONICAL_CONTRACT_FREEZE.md`
- Confirm exact next task and success criteria
- Confirm no regression-risk assumptions are being made implicitly
