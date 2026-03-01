@echo off
REM Aegis-X v3 — 바탕화면에 런처 바로가기 생성 (프로젝트 스크립트 호출)
REM 프로젝트 루트: D:\AEGIS-X_v3
set "DESKTOP=%USERPROFILE%\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%\OneDrive\Desktop"
if not exist "%DESKTOP%" set "DESKTOP=%USERPROFILE%"

set "TARGET=%DESKTOP%\Aegis-X v3 Warroom.bat"
cd /d "%DESKTOP%" 2>nul || exit /b 1

set "ROOT=D:\AEGIS-X_v3"
(
  echo @echo off
  echo call "%ROOT%\scripts\Start_AegisX_With_Browser.bat"
) > "Aegis-X v3 Warroom.bat"

if exist "Aegis-X v3 Warroom.bat" (
  echo Created: %TARGET%
  echo Runs: %ROOT%\scripts\Start_AegisX_With_Browser.bat
  echo Pin to taskbar: Right-click the icon ^> Pin to taskbar
) else (
  echo Failed to create shortcut in: %DESKTOP%
)
pause
