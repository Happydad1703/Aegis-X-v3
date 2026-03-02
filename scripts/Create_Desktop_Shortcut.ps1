# Aegis-X v3 — 바탕화면에 실행 아이콘(.lnk) 생성
# 사용: .\Create_Desktop_Shortcut.ps1
# 또는: powershell -ExecutionPolicy Bypass -File "D:\AEGIS-X_v3\scripts\Create_Desktop_Shortcut.ps1"

$ProjectRoot = if ($PSScriptRoot) { Split-Path $PSScriptRoot -Parent } else { Get-Location }
$Desktop = [Environment]::GetFolderPath("Desktop")
if (-not (Test-Path $Desktop)) {
    $Desktop = Join-Path $env:USERPROFILE "OneDrive\Desktop"
}
if (-not (Test-Path $Desktop)) {
    $Desktop = $env:USERPROFILE
}

$LaunchBat = Join-Path $ProjectRoot "scripts\Start_AegisX_With_Browser.bat"
$ShortcutPath = Join-Path $Desktop "Aegis-X v3 실행.lnk"

try {
    $Wsh = New-Object -ComObject WScript.Shell
    $s = $Wsh.CreateShortcut($ShortcutPath)
    $s.TargetPath = $LaunchBat
    $s.WorkingDirectory = $ProjectRoot
    $s.Description = "Aegis-X v3 시스템 실행 (Backend + Warroom)"
    $s.Save()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($Wsh) | Out-Null
    Write-Host "[OK] Created: $ShortcutPath" -ForegroundColor Green
    Write-Host "    Target: $LaunchBat"
    exit 0
} catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
