param(
  [switch]$SkipWarroomBuild,
  [switch]$SkipDbBootstrap,
  [switch]$SkipMigrate
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$WarroomPath = Join-Path $ProjectRoot "frontend\warroom"
$LoadEnvScript = Join-Path $PSScriptRoot "load_env.ps1"
$MigrateScript = Join-Path $ProjectRoot "scripts\migrate_db_via_url.py"

function Test-TcpPort([string]$HostName, [int]$Port) {
  try {
    $client = New-Object System.Net.Sockets.TcpClient
    $async = $client.BeginConnect($HostName, $Port, $null, $null)
    $ok = $async.AsyncWaitHandle.WaitOne(1200, $false)
    if (-not $ok) {
      $client.Close()
      return $false
    }
    $client.EndConnect($async)
    $client.Close()
    return $true
  } catch {
    return $false
  }
}

function Wait-Http200([string]$Url, [int]$TimeoutSec = 45) {
  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    try {
      $r = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 3
      if ($r.StatusCode -eq 200) { return $true }
    } catch {
      Start-Sleep -Milliseconds 800
    }
  }
  return $false
}

function Test-DockerReady {
  try {
    docker info | Out-Null
    return $true
  } catch {
    return $false
  }
}

function Ensure-DockerReady([int]$TimeoutSec = 120) {
  if (Test-DockerReady) { return $true }

  $dockerDesktop = "C:\Program Files\Docker\Docker\Docker Desktop.exe"
  if (Test-Path $dockerDesktop) {
    Write-Host "Docker daemon 미기동. Docker Desktop 시작 시도..." -ForegroundColor Yellow
    Start-Process $dockerDesktop | Out-Null
  } else {
    Write-Host "Docker Desktop 실행 파일을 찾지 못했습니다: $dockerDesktop" -ForegroundColor DarkYellow
    return $false
  }

  $deadline = (Get-Date).AddSeconds($TimeoutSec)
  while ((Get-Date) -lt $deadline) {
    if (Test-DockerReady) { return $true }
    Start-Sleep -Seconds 3
  }
  return $false
}

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "AEGIS-X v3 Unified Launch (API + Warroom)" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

Set-Location $ProjectRoot
if (Test-Path $LoadEnvScript) {
  & $LoadEnvScript -EnvPath (Join-Path $ProjectRoot ".env")
}

if (-not $SkipDbBootstrap) {
  $dbPort = 5433
  if ($env:DB_PORT -and ($env:DB_PORT -as [int])) {
    $dbPort = [int]$env:DB_PORT
  }

  if (-not (Test-TcpPort "127.0.0.1" $dbPort)) {
    Write-Host "[1/6] DB 포트($dbPort) 미응답. Docker DB 준비..." -ForegroundColor Yellow
    if (-not (Ensure-DockerReady 150)) {
      throw "Docker daemon 준비 실패. Docker Desktop을 먼저 기동해 주세요."
    }

    if ($dbPort -eq 5434) {
      docker compose -f docker-compose.yml -f docker-compose.5434.yml up -d
    } else {
      docker compose up -d
    }

    if (-not (Test-TcpPort "127.0.0.1" $dbPort)) {
      Start-Sleep -Seconds 4
    }
    if (-not (Test-TcpPort "127.0.0.1" $dbPort)) {
      throw "DB 포트($dbPort) 준비 실패."
    }
    Write-Host "[1/6] DB 준비 완료 (port $dbPort)." -ForegroundColor Green
  } else {
    Write-Host "[1/6] DB 이미 실행 중 (port $dbPort)." -ForegroundColor Green
  }
} else {
  Write-Host "[1/6] DB bootstrap 건너뜀 (SkipDbBootstrap)." -ForegroundColor DarkYellow
}

if (-not $SkipMigrate) {
  Write-Host "[2/6] SQL 마이그레이션 적용..." -ForegroundColor Yellow
  if (-not (Test-Path $MigrateScript)) {
    throw "Migration script not found: $MigrateScript"
  }
  python $MigrateScript
  if ($LASTEXITCODE -ne 0) {
    throw "Migration failed. ExitCode=$LASTEXITCODE"
  }
  Write-Host "[2/6] 마이그레이션 완료." -ForegroundColor Green
} else {
  Write-Host "[2/6] 마이그레이션 건너뜀 (SkipMigrate)." -ForegroundColor DarkYellow
}

if (-not (Test-TcpPort "127.0.0.1" 8000)) {
  Write-Host "[3/6] Backend API 시작 (port 8000)..." -ForegroundColor Yellow
  Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$ProjectRoot'; & '$LoadEnvScript' -EnvPath '$ProjectRoot\.env'; uvicorn backend.main:app --host 0.0.0.0 --port 8000 --app-dir ."
} else {
  Write-Host "[3/6] Backend API 이미 실행 중 (port 8000)." -ForegroundColor Green
}

if (-not (Wait-Http200 "http://localhost:8000/healthz" 50)) {
  throw "Backend health check failed: http://localhost:8000/healthz"
}
Write-Host "[4/6] Backend health GREEN." -ForegroundColor Green

Set-Location $WarroomPath
if (-not $SkipWarroomBuild) {
  Write-Host "[5/6] Warroom 프로덕션 빌드..." -ForegroundColor Yellow
  npm run build
} else {
  Write-Host "[5/6] Warroom 빌드 건너뜀 (SkipWarroomBuild)." -ForegroundColor DarkYellow
}

if (-not (Test-TcpPort "127.0.0.1" 3000)) {
  Write-Host "[6/6] Warroom Standalone 시작 (port 3000)..." -ForegroundColor Yellow
  Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$WarroomPath'; npm run start"
} else {
  Write-Host "[6/6] Warroom 이미 실행 중 (port 3000)." -ForegroundColor Green
}

if (-not (Wait-Http200 "http://localhost:3000" 40)) {
  throw "Warroom health check failed: http://localhost:3000"
}

Write-Host "Launch complete. API: http://localhost:8000  Warroom: http://localhost:3000" -ForegroundColor Green
