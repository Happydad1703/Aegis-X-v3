@echo off
REM Aegis-X v3 — Backend 기동 후 브라우저 열기
REM 프로젝트 루트: 이 스크립트 위치의 상위 폴더 (scripts\ 의 부모)
cd /d "%~dp0.."

set "PY=python"
if exist ".venv\Scripts\python.exe" set "PY=.venv\Scripts\python.exe"
if exist "venv\Scripts\python.exe" set "PY=venv\Scripts\python.exe"

REM 이미 8000 포트에서 동작 중인지 확인
powershell -nop -c "try { (New-Object System.Net.Sockets.TcpClient('localhost',8000)).Close(); exit 0 } catch { exit 1 }"
if %errorlevel% equ 0 (
  echo Backend already running. Opening browser...
  start "" "http://localhost:8000/launcher/"
  exit /b 0
)

echo Starting Aegis-X Backend...
start "Aegis-X Backend" cmd /k "cd /d "%~dp0.." && %PY% -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --app-dir ."
echo Waiting 8 seconds for server...
timeout /t 8 /nobreak >nul
start "" "http://localhost:8000/launcher/"
echo Done.
