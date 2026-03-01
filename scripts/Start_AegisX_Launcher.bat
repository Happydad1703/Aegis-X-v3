@echo off
REM Aegis-X v3 — Desktop/Taskbar shortcut: open Launcher in browser
REM Backend must be running (run scripts\run_api.ps1 or: uvicorn backend.main:app --host 0.0.0.0 --port 8000)
start "" "http://localhost:8000/launcher/"
exit /b 0
