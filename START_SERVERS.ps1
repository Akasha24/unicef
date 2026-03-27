# Weather Forecast System - Start Both Servers
# This script starts the backend API and frontend web server in separate terminals

Write-Host "🌡️ Weather Forecast System Startup" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend") -or -not (Test-Path "website")) {
    Write-Host "❌ Error: This script must be run from the project root directory" -ForegroundColor Red
    Write-Host "✓ Project structure verified" -ForegroundColor Green

    # 1) Train
    Write-Host "Running training for 'beed'..." -ForegroundColor Yellow
    try {
        & python -m website.backend.pipeline train --districts beed
    }
    catch {
        Write-Host "Training failed: $_" -ForegroundColor Red
        exit 1
    }

    # 2) Start backend and frontend
    Start-Process powershell -ArgumentList { cd backend; python app.py } -NoNewWindow
    Start-Process powershell -ArgumentList { cd website; python -m http.server 8000 } -NoNewWindow

    # 3) Wait then POST prediction for today
    Start-Sleep -Seconds 5
    Write-Host "Posting a prediction request (district=beed)..." -ForegroundColor Cyan
    $d = (Get-Date).ToString('yyyy-MM-dd')
    try {
        $resp = Invoke-RestMethod -Uri http://localhost:5000/predict -Method Post -ContentType 'application/json' -Body (@{district = 'beed'; date = $d } | ConvertTo-Json)
        $resp | ConvertTo-Json -Depth 5 | Write-Host
    }
    catch {
        Write-Host "Prediction request failed: $_" -ForegroundColor Yellow
    }
    $resp = Invoke-RestMethod -Uri http://localhost:5000/predict -Method Post -ContentType 'application/json' -Body (@{district = 'beed'; date = $d } | ConvertTo-Json)
    Write-Host "Prediction response:" -ForegroundColor Green
    $resp | ConvertTo-Json -Depth 5 | Write-Host
}
catch {
    Write-Host "Prediction request failed: $_" -ForegroundColor Yellow
}
