@echo off
cd /d "%~dp0"
title MoveNet Pose Tracker - Gym AI

echo ======================================================
echo           MoveNet Pose Tracker and Telemetry
echo ======================================================
echo.

python run_movenet.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Script stopped with an error code: %ERRORLEVEL%
    echo Press any key to close this window...
    pause >nul
)
