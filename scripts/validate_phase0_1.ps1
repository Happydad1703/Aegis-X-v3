# scripts/validate_phase0_1.ps1 — Phase 0-1 self-verification harness. Fail fast with clear errors.
# Order: 1) docker ps  2) migrate_db  3) debug_db_target  4) run_engine_cycle  5) docker exec snapshots  6) pytest

$ErrorActionPreference = "Stop"
$ProjectRoot = if ($PSScriptRoot) { Split-Path $PSScriptRoot -Parent } else { Get-Location }
Set-Location $ProjectRoot

Write-Host "=== AEGIS-X V3 Phase 0-1 Validation ===" -ForegroundColor Cyan
Write-Host "PWD: $ProjectRoot"
Write-Host ""

# 1) Docker
Write-Host "[1/6] docker ps (check container)" -ForegroundColor Yellow
$dockerPs = docker ps --format "{{.Names}}" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Docker not running or unavailable. Start Docker Desktop." -ForegroundColor Red
    exit 1
}
if ($dockerPs -notmatch "aegisx-db") {
    Write-Host "[WARN] Container 'aegisx-db' not in 'docker ps'. Run: docker compose up -d" -ForegroundColor Yellow
}
Write-Host "[OK] docker ps" -ForegroundColor Green
Write-Host ""

# 2) Migration
Write-Host "[2/6] migrate_db.ps1" -ForegroundColor Yellow
& "$ProjectRoot\scripts\migrate_db.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Migration failed. Fix migrate_db.ps1 or DB container." -ForegroundColor Red
    exit 2
}
Write-Host "[OK] Migration complete" -ForegroundColor Green
Write-Host ""

# 3) DB target (fallback: migrate via URL if Python uses different DB than container)
Write-Host "[3/6] debug_db_target.py" -ForegroundColor Yellow
python "$ProjectRoot\scripts\debug_db_target.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARN] DB target failed. Trying migrate_db_via_url.py (apply schema to DATABASE_URL target)..." -ForegroundColor Yellow
    python "$ProjectRoot\scripts\migrate_db_via_url.py"
    if ($LASTEXITCODE -eq 0) {
        python "$ProjectRoot\scripts\debug_db_target.py"
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[FAIL] DB target check failed. DATABASE_URL and engine_snapshot. See docs/Execution_Stability_Check_Result.md" -ForegroundColor Red
        exit 3
    }
}
Write-Host "[OK] DB target verified" -ForegroundColor Green
Write-Host ""

# 4) One engine cycle
Write-Host "[4/6] run_engine_cycle.py" -ForegroundColor Yellow
python "$ProjectRoot\scripts\run_engine_cycle.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Engine cycle failed. Check DB connection and snapshot_repo." -ForegroundColor Red
    exit 4
}
Write-Host "[OK] Engine cycle done" -ForegroundColor Green
Write-Host ""

# 5) Snapshots in DB
Write-Host "[5/6] verify_snapshot_keys.py" -ForegroundColor Yellow
python "$ProjectRoot\scripts\verify_snapshot_keys.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Required snapshot keys missing in engine_snapshot." -ForegroundColor Red
    exit 5
}
Write-Host ""

# 6) Pytest
Write-Host "[6/6] pytest (phase0_1 / engine / gate)" -ForegroundColor Yellow
python -m pytest backend/tests/test_phase1_acceptance.py backend/tests/test_contract_engines_purity.py backend/tests/test_combat_force_spec_lock.py -v --tb=short -x 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Tests failed. Fix failing tests." -ForegroundColor Red
    exit 6
}
Write-Host "[OK] Tests passed" -ForegroundColor Green
Write-Host ""
Write-Host "=== Phase 0-1 validation complete ===" -ForegroundColor Cyan
exit 0
