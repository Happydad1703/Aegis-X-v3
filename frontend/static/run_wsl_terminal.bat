@echo off
REM Aegis-X v3 — WSL Terminal (download from Launcher)
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe" (
  start wt -p "Ubuntu"
) else (
  start wsl
)
