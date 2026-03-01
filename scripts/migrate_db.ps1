# scripts/migrate_db.ps1
Write-Host "Applying DB migration..."

# Load .env (simple parser)
$envPath = Join-Path (Get-Location) ".env"
if (Test-Path $envPath) {
  Get-Content $envPath | ForEach-Object {
    if ($_ -match '^\s*#') { return }
    if ($_ -match '^\s*$') { return }
    $kv = $_.Split('=', 2)
    if ($kv.Count -eq 2) {
      $k = $kv[0].Trim()
      $v = $kv[1].Trim()
      if ($k) { Set-Item -Path "Env:$k" -Value $v }
    }
  }
}

# Defaults if missing
$dbUser    = if ($env:DB_USER)     { $env:DB_USER }     else { "postgres" }
$dbName    = if ($env:DB_NAME)     { $env:DB_NAME }     else { "aegisx" }
$container = if ($env:PG_CONTAINER){ $env:PG_CONTAINER }else { "aegisx-db" }

$sqlPath = Join-Path (Get-Location) "db/migrations/001_init_core.sql"
if (!(Test-Path $sqlPath)) {
  throw "Migration SQL not found: $sqlPath"
}

Write-Host "Container = $container"
Write-Host "DB_USER   = $dbUser"
Write-Host "DB_NAME   = $dbName"
Write-Host ""
Write-Host "NOTE: PowerShell does NOT support '< file.sql' redirection like bash. Use pipe." -ForegroundColor Yellow

# Pipe SQL into psql inside container (001 then 002 if present)
Get-Content $sqlPath -Raw | docker exec -i $container psql -U $dbUser -d $dbName
if ($LASTEXITCODE -ne 0) { throw "Migration 001 failed. ExitCode=$LASTEXITCODE" }

$sqlPath2 = Join-Path (Get-Location) "db/migrations/002_order_log.sql"
if (Test-Path $sqlPath2) {
  Get-Content $sqlPath2 -Raw | docker exec -i $container psql -U $dbUser -d $dbName
  if ($LASTEXITCODE -ne 0) { throw "Migration 002 failed. ExitCode=$LASTEXITCODE" }
}

Write-Host "Migration complete."
