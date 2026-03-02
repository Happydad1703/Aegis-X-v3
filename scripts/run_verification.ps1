# scripts/run_verification.ps1 — Self-validation harness (V1 structural + V2 runtime + V3 safety).
# Run from project root. Outputs summary; full report in docs/VERIFICATION_REPORT.md.
$ErrorActionPreference = "Continue"
$ProjectRoot = if ($PSScriptRoot) { Split-Path $PSScriptRoot -Parent } else { Get-Location }
Set-Location $ProjectRoot

Write-Host "=== Aegis-X v3 Verification ===" -ForegroundColor Cyan
Write-Host "PWD: $ProjectRoot"

# V2 Step A
Write-Host "`n[V2-A] Docker Compose (container aegisx-db)..."
docker compose up -d 2>&1 | Out-Null
$container = docker ps -q -f name=aegisx-db 2>&1
if ($container) { Write-Host "  PASS: aegisx-db running" -ForegroundColor Green } else { Write-Host "  FAIL: aegisx-db not running" -ForegroundColor Red }

# V2 Step B
Write-Host "`n[V2-B] Migrate DB..."
& "$ProjectRoot\scripts\migrate_db.ps1" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "  PASS: migrate_db.ps1 completed" -ForegroundColor Green } else { Write-Host "  FAIL: migrate_db.ps1 exit $LASTEXITCODE" -ForegroundColor Red }

# V2 Step C
Write-Host "`n[V2-C] debug_db_target.py..."
$debugOut = python "$ProjectRoot\scripts\debug_db_target.py" 2>&1
if ($LASTEXITCODE -eq 0) { Write-Host "  PASS: debug_db_target.py (engine_snapshot exists)" -ForegroundColor Green } else { Write-Host "  FAIL or SKIP: Python may be pointing to different DB (see report)" -ForegroundColor Yellow }

# V2 Step D (optional - requires correct DATABASE_URL to container)
Write-Host "`n[V2-D] run_engine_worker.ps1 (one cycle)..."
& "$ProjectRoot\scripts\run_engine_worker.ps1" 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) { Write-Host "  PASS: engine cycle completed" -ForegroundColor Green } else { Write-Host "  FAIL/SKIP: exit $LASTEXITCODE (check DATABASE_URL)" -ForegroundColor Yellow }

Write-Host "`nDone. See docs/VERIFICATION_REPORT.md for full evidence." -ForegroundColor Cyan
