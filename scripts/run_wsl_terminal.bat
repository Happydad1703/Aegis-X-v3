@echo off
REM Aegis-X v3 — WSL Terminal shortcut (taskbar/desktop)
REM Windows Terminal preferred; falls back to wsl.exe
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe" (
  start wt -p "Ubuntu"
) else (
  start wsl
)
