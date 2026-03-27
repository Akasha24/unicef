@echo off
REM Weather Forecast System - Start Both Servers
REM This batch script starts the backend API and frontend web server in separate windows

echo.
echo ========================================
echo   Weather Forecast System Startup
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "backend\" (
    echo Error: backend folder not found
    echo This script must be run from the project root directory
    echo.
    echo Expected structure:
    echo   unicef/
    echo   └── website/
    echo.
    pause
    exit /b 1
)

if not exist "website\" (
    echo Error: website folder not found
    echo This script must be run from the project root directory
    echo.
    echo Expected structure:
    echo   unicef/
    echo   └── website/
    echo.
    pause
    exit /b 1
)

echo [OK] Project structure verified

REM 1) Train (creates models/scalers)
echo Running training for 'beed'...
python -m website.backend.pipeline train --districts beed
if ERRORLEVEL 1 (
    echo Training failed. Aborting.
    exit /b 1
)

REM 2) Start backend and frontend in new windows
start "Backend" cmd /k cd backend ^& python app.py
start "Frontend" cmd /k cd website ^& python -m http.server 8000

REM 3) Wait briefly then POST a prediction for today
timeout /t 5 /nobreak
powershell -NoProfile -Command "$d=(Get-Date).ToString('yyyy-MM-dd'); Invoke-RestMethod -Uri 'http://localhost:5000/predict' -Method Post -ContentType 'application/json' -Body (ConvertTo-Json @{district='beed'; date=$d}) | ConvertTo-Json -Depth 5"

echo Done.
pause
