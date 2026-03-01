# Aegis-X v3 — 시스템 전체 실행 안정성 점검
# 프로젝트 루트: D:\AEGIS-X_v3 | Phase 0-1 + 계약테스트 + 내부시뮬레이션
$ErrorActionPreference = "Continue"
$ProjectRoot = "D:\AEGIS-X_v3"
$results = @()

function Record-Step {
    param([string]$Name, [bool]$Ok, [string]$Detail = "")
    $script:results += [PSCustomObject]@{ Step = $Name; Pass = $Ok; Detail = $Detail }
    $color = if ($Ok) { "Green" } else { "Red" }
    $status = if ($Ok) { "PASS" } else { "FAIL" }
    Write-Host "[$status] $Name" -ForegroundColor $color
    if ($Detail) { Write-Host "   $Detail" -ForegroundColor Gray }
}

Set-Location $ProjectRoot
Write-Host "`n=== Aegis-X v3 실행 안정성 점검 ===" -ForegroundColor Cyan
Write-Host "루트: $ProjectRoot`n" -ForegroundColor Gray

# 1) Docker / DB 컨테이너
Write-Host "1. Docker DB 컨테이너 확인..." -ForegroundColor Yellow
try {
    $cid = docker ps -q -f "name=aegisx-db" 2>$null
    if ($cid) {
        Record-Step -Name "Docker DB (aegisx-db)" -Ok $true -Detail "실행 중"
    } else {
        docker compose up -d 2>&1 | Out-Null
        Start-Sleep -Seconds 3
        $cid = docker ps -q -f "name=aegisx-db" 2>$null
        Record-Step -Name "Docker DB (aegisx-db)" -Ok ($null -ne $cid) -Detail $(if (-not $cid) { "기동 실패 또는 docker 미설치" })
    }
} catch {
    Record-Step -Name "Docker DB (aegisx-db)" -Ok $false -Detail $_.Exception.Message
}

# 2) 마이그레이션
Write-Host "`n2. DB 마이그레이션 적용..." -ForegroundColor Yellow
try {
    & "$ProjectRoot\scripts\migrate_db.ps1" 2>&1 | Out-Null
    Record-Step -Name "마이그레이션 (migrate_db.ps1)" -Ok ($LASTEXITCODE -eq 0) -Detail $(if ($LASTEXITCODE -ne 0) { "exit $LASTEXITCODE" })
} catch {
    Record-Step -Name "마이그레이션 (migrate_db.ps1)" -Ok $false -Detail $_.Exception.Message
}

# 3) 테이블 존재 확인
Write-Host "`n3. 테이블 목록 확인..." -ForegroundColor Yellow
try {
    $tables = (docker exec aegisx-db psql -U postgres -d aegisx -t -c "\dt" 2>&1) | Out-String
    $hasEngineSnapshot = [bool]($tables -match "engine_snapshot")
    Record-Step -Name "테이블 (engine_snapshot 등)" -Ok $hasEngineSnapshot -Detail $(if (-not $hasEngineSnapshot) { "테이블 없음 또는 docker 실패" })
} catch {
    Record-Step -Name "테이블 (engine_snapshot 등)" -Ok $false -Detail $_.Exception.Message
}

# 4) Python DB 접속 대상 진단
Write-Host "`n4. Python DB 접속 진단 (debug_db_target.py)..." -ForegroundColor Yellow
try {
    $out = python "$ProjectRoot\scripts\debug_db_target.py" 2>&1
    $ok = $LASTEXITCODE -eq 0 -and ($out -match "current_database|engine_snapshot")
    Record-Step -Name "Python DB 대상 진단" -Ok $ok -Detail $(if (-not $ok) { $out | Select-Object -First 3 })
} catch {
    Record-Step -Name "Python DB 대상 진단" -Ok $false -Detail $_.Exception.Message
}

# 5) 엔진 1회 사이클 (실패 시 마이그레이션 재실행 후 1회 재시도)
Write-Host "`n5. 엔진 1회 사이클 (run_engine_worker.ps1)..." -ForegroundColor Yellow
$engineOk = $false
$engineOut = & "$ProjectRoot\scripts\run_engine_worker.ps1" 2>&1
if ($LASTEXITCODE -eq 0) { $engineOk = $true }
if (-not $engineOk -and ($engineOut -match "does not exist|UndefinedTable")) {
    Write-Host "   마이그레이션 재실행 후 엔진 재시도..." -ForegroundColor Gray
    & "$ProjectRoot\scripts\migrate_db.ps1" 2>&1 | Out-Null
    $engineOut = & "$ProjectRoot\scripts\run_engine_worker.ps1" 2>&1
    if ($LASTEXITCODE -eq 0) { $engineOk = $true }
}
if ($engineOk) {
    Record-Step -Name "엔진 1사이클" -Ok $true -Detail ""
} else {
    $errPreview = ($engineOut | Select-Object -First 5) -join " "
    if ($errPreview.Length -gt 120) { $errPreview = $errPreview.Substring(0, 120) + "..." }
    Record-Step -Name "엔진 1사이클" -Ok $false -Detail $errPreview
}

# 6) 스냅샷 적재 확인
Write-Host "`n6. 스냅샷 적재 확인..." -ForegroundColor Yellow
try {
    $snapStr = (docker exec aegisx-db psql -U postgres -d aegisx -t -c "SELECT COUNT(*) FROM engine_snapshot WHERE generated_at > NOW() - INTERVAL '5 minutes';" 2>&1) | Out-String
    $count = 0
    if ($snapStr -match '(\d+)') { $count = [int]$Matches[1] }
    $ok = $count -ge 6
    Record-Step -Name "스냅샷 최근 5분 내 6건 이상" -Ok $ok -Detail "count=$count"
} catch {
    Record-Step -Name "스냅샷 최근 5분 내 6건 이상" -Ok $false -Detail $_.Exception.Message
}

# 7) 계약 테스트 (pytest) — 4개 통과 + test_engine_loop 스킵/통과 시 성공
Write-Host "`n7. 계약 테스트 (pytest)..." -ForegroundColor Yellow
try {
    $pytestOut = & python -m pytest `
        "$ProjectRoot\backend\tests\test_contract_api_db_only_read.py" `
        "$ProjectRoot\backend\tests\test_contract_ui_never_calls_compute.py" `
        "$ProjectRoot\backend\tests\test_contract_single_write_path.py" `
        "$ProjectRoot\backend\tests\test_contract_engines_purity.py" `
        "$ProjectRoot\backend\tests\test_engine_loop.py" `
        -v --tb=short 2>&1
    $outStr = $pytestOut | Out-String
    $pytestOk = ($LASTEXITCODE -eq 0) -or ($outStr -match "4 passed.*1 skipped")
    Record-Step -Name "계약 테스트 (5개)" -Ok $pytestOk -Detail $(if (-not $pytestOk) { "exit $LASTEXITCODE" })
    if (-not $pytestOk) { $pytestOut | Select-Object -Last 15 | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray } }
} catch {
    Record-Step -Name "계약 테스트 (5개)" -Ok $false -Detail $_.Exception.Message
}

# 8) 내부 시뮬레이션 (아키텍처/스냅샷 키)
Write-Host "`n8. 내부 시뮬레이션 (internal_simulation.py)..." -ForegroundColor Yellow
try {
    $simOut = python "$ProjectRoot\scripts\internal_simulation.py" 2>&1
    $simOk = $LASTEXITCODE -eq 0 -and ($simOut -match "GO|PASS")
    Record-Step -Name "내부 시뮬레이션" -Ok $simOk -Detail $(if (-not $simOk) { "Report 확인: docs/Internal_Simulation_Report.md" })
} catch {
    Record-Step -Name "내부 시뮬레이션" -Ok $false -Detail $_.Exception.Message
}

# 9) (선택) 외부 통신 점검
Write-Host "`n9. 외부 API 통신 점검 (check_comm.py)..." -ForegroundColor Yellow
try {
    $commOut = python "$ProjectRoot\scripts\check_comm.py" 2>&1
    $commOk = $LASTEXITCODE -eq 0
    Record-Step -Name "외부 통신 (check_comm)" -Ok $commOk -Detail "환경변수 미설정 시 SKIP 가능"
} catch {
    Record-Step -Name "외부 통신 (check_comm)" -Ok $false -Detail $_.Exception.Message
}

# 요약
$passed = ($results | Where-Object { $_.Pass }).Count
$total  = $results.Count
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "결과: $passed / $total 항목 통과" -ForegroundColor $(if ($passed -eq $total) { "Green" } else { "Yellow" })
if ($passed -lt $total) {
    Write-Host "실패 항목:" -ForegroundColor Red
    $results | Where-Object { -not $_.Pass } | ForEach-Object { Write-Host "  - $($_.Step)" }
}
Write-Host "참고: 계약 테스트 5번(test_engine_loop) 통과하려면 pip install asyncpg 필요." -ForegroundColor Gray
Write-Host "참고: 엔진/스냅샷 실패 시 .env의 DATABASE_URL과 마이그레이션 대상 DB가 동일한지 확인." -ForegroundColor Gray
if ($passed -lt $total) {
    Write-Host "자체 해결 불가 시: docs\Stability_Check_Report_Unresolvable.md 참조." -ForegroundColor Yellow
}
Write-Host "========================================`n" -ForegroundColor Cyan

exit $(if ($passed -eq $total) { 0 } else { 1 })
