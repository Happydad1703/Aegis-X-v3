# scripts/run_engine_worker.ps1 — Phase 0/1: one engine cycle (sync). Run from any dir; cd to project root.
$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot
Write-Host "Running one engine cycle... PWD: $((Get-Location).Path)"
python .\scripts\run_engine_cycle.py
