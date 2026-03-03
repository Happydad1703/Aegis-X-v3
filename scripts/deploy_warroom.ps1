param(
  [switch]$SkipInstall,
  [switch]$SkipBuild,
  [switch]$NoStart
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path $PSScriptRoot -Parent
$WarroomPath = Join-Path $ProjectRoot "frontend\warroom"
$LoadEnvScript = Join-Path $PSScriptRoot "load_env.ps1"

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "AEGIS-X v3 Warroom CIC: Production Deployment" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Project Root : $ProjectRoot"
Write-Host "Warroom Path : $WarroomPath"

if (-not (Test-Path $WarroomPath)) {
  throw "Warroom path not found: $WarroomPath"
}

if (Test-Path $LoadEnvScript) {
  & $LoadEnvScript -EnvPath (Join-Path $ProjectRoot ".env")
}

Set-Location $WarroomPath

if (-not $SkipInstall) {
  Write-Host "[1/3] 의존성 설치/동기화..." -ForegroundColor Yellow
  npm install
}
else {
  Write-Host "[1/3] 의존성 설치 건너뜀 (SkipInstall)" -ForegroundColor DarkYellow
}

if (-not $SkipBuild) {
  Write-Host "[2/3] 프로덕션 빌드 수행..." -ForegroundColor Yellow
  npm run build
}
else {
  Write-Host "[2/3] 빌드 건너뜀 (SkipBuild)" -ForegroundColor DarkYellow
}

if ($NoStart) {
  Write-Host "[3/3] 서버 기동 건너뜀 (NoStart)" -ForegroundColor DarkYellow
  exit 0
}

Write-Host "[3/3] Warroom CIC 서버 기동 (Standalone, Port 3000)..." -ForegroundColor Green
npm run start
