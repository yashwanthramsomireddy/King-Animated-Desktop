@echo off
setlocal
title Build King Animated Desktop installer
cd /d "%~dp0"
echo ============================================
echo  King Animated Desktop - build Windows installer
echo  Output: dist\KingAnimatedDesktop_Setup_1.0.0.exe
echo ============================================
echo.

echo [1/4] Installing build dependencies (PySide6, PyInstaller)...
python -m pip install --upgrade pip >nul
python -m pip install PySide6 pyinstaller pillow
if errorlevel 1 goto :fail

echo.
echo [2/4] Packaging KingAnimatedDesktop.exe with PyInstaller...
python -m PyInstaller run.py --name KingAnimatedDesktop --noconsole --noconfirm --clean ^
  --icon assets\king_animated_desktop.ico --distpath dist --workpath build ^
  --exclude-module PySide6.QtWebEngineCore --exclude-module PySide6.QtWebEngineWidgets ^
  --exclude-module PySide6.Qt3DCore --exclude-module PySide6.QtQuick --exclude-module PySide6.QtQml ^
  --exclude-module PySide6.QtMultimedia --exclude-module PySide6.QtCharts --exclude-module PySide6.QtDataVisualization
if errorlevel 1 goto :fail

echo.
echo [3/4] Looking for Inno Setup (ISCC.exe)...
set "ISCC="
call :findiscc
if not defined ISCC (
  echo Inno Setup not found - installing it with winget...
  winget install --id JRSoftware.InnoSetup -e --accept-source-agreements --accept-package-agreements
  call :findiscc
)
if not defined ISCC (
  echo.
  echo Could not find Inno Setup. Install it from https://jrsoftware.org/isdl.php
  echo ^(any 6.x version, default options^), then run this file again.
  goto :fail
)
echo Using: %ISCC%
if not exist "dist\KingAnimatedDesktop\KingAnimatedDesktop.exe" (
  echo dist\KingAnimatedDesktop\KingAnimatedDesktop.exe is missing - the PyInstaller step did not finish.
  goto :fail
)

echo.
echo [4/4] Building installer...
"%ISCC%" /DAppVersion=1.0.0 "%~dp0installer\KingAnimatedDesktop.iss"
if errorlevel 1 goto :fail

echo.
echo DONE!  Installer: %~dp0dist\KingAnimatedDesktop_Setup_1.0.0.exe
explorer "%~dp0dist"
pause
exit /b 0

:fail
echo.
echo BUILD FAILED - see messages above.
pause
exit /b 1

:findiscc
for %%D in ("%ProgramFiles(x86)%" "%ProgramFiles%" "%LOCALAPPDATA%\Programs") do (
  for /d %%I in ("%%~D\Inno Setup*") do (
    if exist "%%~I\ISCC.exe" set "ISCC=%%~I\ISCC.exe"
  )
)
if not defined ISCC for /f "delims=" %%I in ('where iscc 2^>nul') do set "ISCC=%%I"
exit /b 0
