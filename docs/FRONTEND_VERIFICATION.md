# Frontend Verification

Checklist and run method for Warroom/CIC.

## Static (code)

- No regime/risk/allocation/score calculation in UI (grep for sharpe, dd, regime formula in app/components/lib).
- Snapshot rendering uses snapshot_data as-is; field names preserved.
- No API keys in frontend; only NEXT_PUBLIC_API_BASE_URL.

## Integration (runtime)

- API down: UI shows DISCONNECTED/DEGRADED; no crash.
- Health + snapshot OK: header and Home show last updated, freshness.
- Freshness RED: control buttons disabled; overlay or message.
- One snapshot key missing: other panels OK; failed panel shows error + retry.

## E2E (Playwright)

1. / loads (Warroom Home).
2. / shows 6 core snapshot areas.
3. /regime loads.
4. API down mock -> header shows DISCONNECTED, app does not crash.
5. Freshness RED mock -> read-only lock + control buttons disabled.

Run: `cd frontend/warroom && npx playwright install chromium && npm run test:e2e`

## Run commands

Backend: `python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000`
Frontend: `cd frontend/warroom && echo NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 > .env.local && npm run dev`

Build: `npm run build && npm run start`
