# scripts/run_engine_worker.ps1
Write-Host "Running one engine cycle..."
Write-Host "PWD: $((Get-Location).Path)"
python .\scripts\run_engine_cycle.py
