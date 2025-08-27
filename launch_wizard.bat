@echo off
title Professional Image Quality Analyzer - Tabbed Interface
echo.
echo ====================================================
echo   Professional Image Quality Analyzer - 3-Tab Interface
echo ====================================================
echo.
echo Starting professional tabbed interface...
echo.
echo Features:
echo - Tab 1: Upload your image file
echo - Tab 2: Configure quality standards  
echo - Tab 3: Run analysis and view results
echo - Professional dark text interface
echo - Complete offline security
echo.

cd /d "%~dp0"
python tabbed_analyzer.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Failed to start the analyzer.
    echo Please ensure Python and required packages are installed.
    echo.
    pause
)
