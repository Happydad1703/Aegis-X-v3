$ProjectRoot = if ($PSScriptRoot) { Split-Path $PSScriptRoot -Parent } else { Get-Location }
$Desktop = [Environment]::GetFolderPath("Desktop")
if (-not (Test-Path $Desktop)) {
    $Desktop = Join-Path $env:USERPROFILE "OneDrive\Desktop"
}
if (-not (Test-Path $Desktop)) {
    $Desktop = $env:USERPROFILE
}

$ShortcutPath = Join-Path $Desktop "Aegis-X v3 통합실행.lnk"
$PowerShellExe = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
$LaunchScript = Join-Path $ProjectRoot "scripts\launch_aegis_v3.ps1"
$Args = "-NoProfile -ExecutionPolicy Bypass -File `"$LaunchScript`""

try {
    $Wsh = New-Object -ComObject WScript.Shell
    $s = $Wsh.CreateShortcut($ShortcutPath)
    $s.TargetPath = $PowerShellExe
    $s.Arguments = $Args
    $s.WorkingDirectory = $ProjectRoot
    $s.Description = "Aegis-X v3 통합 실행 (DB/API/Warroom)"
    $s.Save()
    [System.Runtime.Interopservices.Marshal]::ReleaseComObject($Wsh) | Out-Null
    Write-Host "[OK] Created: $ShortcutPath" -ForegroundColor Green
    Write-Host "    Target: $PowerShellExe"
    Write-Host "    Args  : $Args"
    exit 0
} catch {
    Write-Host "[FAIL] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
