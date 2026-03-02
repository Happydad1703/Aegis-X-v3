# scripts/run_engine_comm_check.ps1 — 뉴스 소화 엔진 통신점검 (외부 API + 수집 + 엔진 + 스냅샷 확인)
$ProjectRoot = if ($PSScriptRoot) { Split-Path $PSScriptRoot -Parent } else { Get-Location }
Set-Location $ProjectRoot
python scripts/run_engine_comm_check.py
exit $LASTEXITCODE
