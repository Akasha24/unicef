# Weather Forecast System - Start Both Servers
# This script starts the backend API and frontend web server in separate terminals

Write-Host "🌡️ Weather Forecast System Startup" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "website")) {
    Write-Host "❌ Error: This script must be run from the project root directory" -ForegroundColor Red
    Write-Host "Expected structure: unicef/" -ForegroundColor Red
    Write-Host "  ├── backend/" -ForegroundColor Red
    Write-Host "  └── website/" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Project structure verified" -ForegroundColor Green
Write-Host ""

# Start backend server
Write-Host "Starting Backend API (port 5000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList {
    cd backend
    python app.py
} -NoNewWindow

Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start frontend server
Write-Host "Starting Frontend Server (port 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList {
    cd website
    python -m http.server 8000
} -NoNewWindow

Write-Host "⏳ Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "✅ Both servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "Access points:" -ForegroundColor Cyan
Write-Host "  📱 Main App:    http://localhost:8000" -ForegroundColor Green
Write-Host "  🔧 Diagnostics: http://localhost:8000/diagnostic.html" -ForegroundColor Green
Write-Host "  🔌 Backend API: http://localhost:5000" -ForegroundColor Green
Write-Host "  ❤️ Health Check: http://localhost:5000/health" -ForegroundColor Green
Write-Host ""
Write-Host "Keyboard shortcuts:" -ForegroundColor Cyan
Write-Host "  Press Ctrl+C in each terminal to stop the servers" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Cyan
Write-Host "  • Start with http://localhost:8000/diagnostic.html to verify setup" -ForegroundColor White
Write-Host "  • If servers don't respond, ensure ports 5000 and 8000 are available" -ForegroundColor White
Write-Host "  • Check Python is installed: python --version" -ForegroundColor White
Write-Host ""
