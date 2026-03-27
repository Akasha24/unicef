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
    echo   ├── backend/
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
    echo   ├── backend/
    echo   └── website/
    echo.
    pause
    exit /b 1
)

echo [OK] Project structure verified
echo.

REM Start backend server
echo Starting Backend API on port 5000...
start "Backend API (Port 5000)" cmd /k cd backend ^& python app.py

REM Wait a few seconds for backend to start
timeout /t 3 /nobreak

REM Start frontend server
echo Starting Frontend Server on port 8000...
start "Frontend Server (Port 8000)" cmd /k cd website ^& python -m http.server 8000

REM Wait for frontend to start
timeout /t 2 /nobreak

echo.
echo ========================================
echo   Both servers are starting!
echo ========================================
echo.
echo Access points:
echo   Main App:    http://localhost:8000
echo   Diagnostics: http://localhost:8000/diagnostic.html
echo   Backend API: http://localhost:5000
echo   Health Check: http://localhost:5000/health
echo.
echo Tips:
echo   1. Close any window to stop that server
echo   2. Use Ctrl+C in each window to stop gracefully
echo   3. Both windows will stay open so you can see server logs
echo.
echo Next steps:
echo   1. Open http://localhost:8000 in your browser
echo   2. Or try diagnostics at http://localhost:8000/diagnostic.html
echo.
pause
