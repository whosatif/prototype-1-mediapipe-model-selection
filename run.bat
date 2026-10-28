@echo off
cd /d "%~dp0"
title MediaPipe Pose Tracker - Gym AI

echo ======================================================
echo           MediaPipe Pose Landmarker & Telemetry
echo ======================================================
echo.

python run_webcam.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Script stopped with an error code: %ERRORLEVEL%
    echo Press any key to close this window...
    pause >nul
)
