$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$LoadEnvScript = Join-Path $PSScriptRoot "load_env.ps1"
$EnvPath = Join-Path $ProjectRoot ".env"

if (-not (Test-Path $LoadEnvScript)) {
  throw "Missing loader script: $LoadEnvScript"
}

& $LoadEnvScript -EnvPath $EnvPath

Write-Host "Current env summary:" -ForegroundColor Cyan
Write-Host "  DATABASE_URL      = $env:DATABASE_URL"
Write-Host "  ASYNC_DATABASE_URL= $env:ASYNC_DATABASE_URL"
Write-Host "  DB_HOST           = $env:DB_HOST"
Write-Host "  DB_PORT           = $env:DB_PORT"
Write-Host "  DB_NAME           = $env:DB_NAME"
Write-Host "  DB_USER           = $env:DB_USER"
