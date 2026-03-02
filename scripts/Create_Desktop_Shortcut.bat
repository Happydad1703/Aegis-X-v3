@echo off
REM Aegis-X v3 — 바탕화면에 실행 아이콘(바로가기) 생성
REM 프로젝트 루트: 이 스크립트(scripts\) 위치의 상위 폴더
for %%I in ("%~dp0..") do set "ROOT=%%~fI"
set "DESKTOP=%USERPROFILE%\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\OneDrive\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%"

cd /d "%DESKTOP%" 2>nul || exit /b 1

REM 1) 실행용 .bat 생성 (기존 호환)
set "BATFILE=Aegis-X v3 Warroom.bat"
(
  echo @echo off
  echo call "%ROOT%\scripts\Start_AegisX_With_Browser.bat"
) > "%BATFILE%"

REM 2) .lnk 실행 아이콘 생성 (PowerShell 스크립트 호출)
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%\scripts\Create_Desktop_Shortcut.ps1"

if exist "%BATFILE%" (
  echo [OK] Created: %DESKTOP%\%BATFILE%
)
echo.
echo 바탕화면에 다음이 생성되었습니다:
echo   - Aegis-X v3 Warroom.bat
echo   - Aegis-X v3 실행.lnk ^(실행 아이콘^)
echo 작업 표시줄 고정: 아이콘 우클릭 -^> 작업 표시줄에 고정
echo.
pause
