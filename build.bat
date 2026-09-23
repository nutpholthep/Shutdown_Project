@echo off
title Build Shutdown Scheduler (.EXE)
echo ========================================================
echo   Building Shutdown Scheduler with Anti-SmartBlock...
echo ========================================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0build_and_sign.ps1"

echo.
echo Press any key to exit...
pause >nul
