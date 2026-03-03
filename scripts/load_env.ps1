param(
  [string]$EnvPath
)

$ErrorActionPreference = "Stop"

if (-not $EnvPath -or [string]::IsNullOrWhiteSpace($EnvPath)) {
  $ProjectRoot = Split-Path $PSScriptRoot -Parent
  $EnvPath = Join-Path $ProjectRoot ".env"
}

if (-not (Test-Path $EnvPath)) {
  Write-Host "[WARN] .env not found: $EnvPath" -ForegroundColor DarkYellow
  return
}

Get-Content $EnvPath | ForEach-Object {
  $line = $_.Trim()
  if ([string]::IsNullOrWhiteSpace($line)) { return }
  if ($line.StartsWith("#")) { return }

  $parts = $line.Split("=", 2)
  if ($parts.Count -ne 2) { return }

  $key = $parts[0].Trim()
  $value = $parts[1].Trim()
  if ([string]::IsNullOrWhiteSpace($key)) { return }

  # Remove optional wrapping quotes.
  if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
    $value = $value.Substring(1, $value.Length - 2)
  }

  Set-Item -Path "Env:$key" -Value $value
}

Write-Host "[OK] Loaded environment from $EnvPath" -ForegroundColor Green
