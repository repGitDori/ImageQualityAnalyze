@echo off
title Professional Image Quality Analyzer
echo.
echo ========================================
echo   Professional Image Quality Analyzer
echo ========================================
echo.
echo Starting tabbed interface...
echo.
echo 📁 Tab 1: Upload Image
echo ⚙️ Tab 2: Configure Standards
echo 📊 Tab 3: Analyze Results  
echo.
echo 🔒 100%% Secure • Offline Operation
echo.

cd /d "%~dp0"
C:/Users/Lapi/.virtualenvs/Documents-P0JnTrLx/Scripts/python.exe tabbed_analyzer.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start the analyzer.
    pause
)
