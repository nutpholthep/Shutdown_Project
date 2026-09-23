@echo off
title Fix Smart Block - Shutdown Scheduler
echo ========================================================
echo   Fixing Smart Block / Windows SmartScreen...
echo ========================================================
echo.

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0unblock_app.ps1"

echo.
echo Press any key to exit...
pause >nul
