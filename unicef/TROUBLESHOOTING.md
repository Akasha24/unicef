# System Setup & Troubleshooting Guide

## Quick Start (3 Steps)

### Step 1: Navigate to Project
```bash
cd c:\Users\ACER\projects\unicef
```

### Step 2: Start Backend (Terminal 1)
```bash
cd backend
python app.py
```
✓ You should see: `Running on http://127.0.0.1:5000`

### Step 3: Start Frontend (Terminal 2)
```bash
cd website
python -m http.server 8000
```
✓ You should see: `Serving HTTP on 0.0.0.0 port 8000`

### Step 4: Open Application
- **Main App**: http://localhost:8000
- **Diagnostics**: http://localhost:8000/diagnostic.html
- **Backend Health**: http://localhost:5000/health

---

## Debugging: The System isn't Working

### 1. Check Backend is Running

**Problem**: "Fetch failed: TypeError: Failed to fetch"

**Solution**:
1. Ensure backend terminal shows: `Running on http://127.0.0.1:5000`
2. Test manually: Open http://localhost:5000/health in browser
3. Expected result: `{"status":"healthy","service":"weather-forecast-api","version":"1.0.0"}`

If Step 3 fails:
- Backend isn't running → Run `python app.py` in backend folder
- Port 5000 in use → Kill process or restart
- Module not found → Run `pip install -r requirements.txt`

### 2. Check Frontend is Running

**Problem**: Page doesn't load at http://localhost:8000

**Solution**:
1. Ensure frontend terminal shows: `Serving HTTP on 0.0.0.0 port 8000`
2. Check for errors in terminal
3. Try refreshing page (Ctrl+F5 for hard refresh)

### 3. Verify Connectivity

**Problem**: Districts dropdown shows "⚠️ Offline"

**Solution**:
1. Open browser Developer Tools: F12
2. Go to Console tab
3. Look for error messages starting with ❌
4. Common errors:
   - "Failed to fetch" = Backend not running or wrong port
   - "CORS error" = Backend CORS not configured
   - "404 Not Found" = Wrong API endpoint

### 4. Check Browser Console for Debugging

**How to access**:
- Press F12 → Console tab
- Look for log messages starting with `[FORECAST]`
- Look for error messages starting with ❌

**Debug messages show**:
- API_BASE_URL being used
- Whether backend is reachable
- Districts loaded/failed
- Prediction requests/responses
- Detailed error information

### 5. Run Diagnostic Tool

**Access**: http://localhost:8000/diagnostic.html

This tool automatically checks:
- ✓ Frontend page loads
- ✓ JavaScript libraries loaded
- ✓ API_BASE_URL configured correctly
- ✓ Backend /health endpoint responding
- ✓ /api/districts endpoint working
- ✓ /api/model-info endpoint working
- ✓ Model files exist

Each check shows:
- ✓ Pass (green) - Component working
- ✗ Fail (red) - Component not working, click for details
- ⏳ Loading - Test in progress

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'tensorflow'"

**Cause**: Dependencies not installed

**Solution**:
```bash
pip install -r requirements.txt
```

Then restart backend: `python app.py`

### Issue: "Address already in use: port 5000"

**Cause**: Another process (or previous instance) using the port

**Solution**:

**Option 1: Kill the process**
```bash
# PowerShell
Get-Process -Name python | Stop-Process -Force

# Or find which process uses port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Option 2: Use different port**
Edit `backend/app.py`, change:
```python
if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Change 5000 to 5001
```
Then update `website/script.js`:
```javascript
const API_BASE_URL = 'http://localhost:5001';  // Update port here
```

### Issue: "CORS error" in browser console

**Cause**: Backend CORS not properly configured

**Solution**:
1. Check `backend/app.py` has:
```python
from flask_cors import CORS
CORS(app, 
     origins="*",
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type"],
     expose_headers=["Content-Type"],
     supports_credentials=False,
     max_age=3600)
```

2. If missing, add the above code after `app = Flask(__name__)`
3. Restart backend

### Issue: "FileNotFoundError: Model files not found"

**Cause**: Model files (.keras, .pkl) missing from backend folder

**Solution**:
1. Verify files exist in `backend/` folder:
   - `weather_model_beed.keras`
   - `weather_scaler_beed.pkl`
   - (and any other district files)

2. If missing, regenerate by training:
```bash
cd backend
python train_model.py
```

3. Restart backend: `python app.py`

### Issue: "No districts available"

**Cause**: Model files not found or config missing

**Solution**:
1. Run diagnostic tool at http://localhost:8000/diagnostic.html
2. Check Model Files section - should show files exist
3. If showing ✗, regenerate with `python train_model.py`
4. Verify `backend/config.py` has district definitions

### Issue: Predictions work but results look wrong

**Cause**: Model not properly trained or outdated

**Solution**:
1. Retrain the model:
```bash
cd backend
python train_model.py
```

2. Restart backend: `python app.py`
3. Try prediction again

---

## File Structure Reference

```
unicef/
│
├── backend/                           # Backend API
│   ├── app.py                         # Flask app, 5+ API endpoints
│   ├── models.py                      # Model management, prediction logic  
│   ├── config.py                      # Configuration, district info
│   ├── train_model.py                 # Model training script
│   ├── requirements.txt               # Python dependencies
│   ├── weather_model_beed.keras       # Trained model (created by train_model.py)
│   ├── weather_scaler_beed.pkl        # Data scaler (created by train_model.py)
│   └── [other model files...]         # Models for other districts
│
├── website/                           # Frontend application
│   ├── index.html                     # Main app page
│   ├── style.css                      # Styling
│   ├── script.js                      # JavaScript, API communication
│   └── diagnostic.html                # Diagnostic tool
│
├── readme.md                          # Project overview
├── SETUP_CHECKLIST.md                 # Setup verification guide
├── TROUBLESHOOTING.md                 # This file
└── START_SERVERS.ps1                  # PowerShell startup script
```

---

## Configuration Files

### backend/config.py
Contains:
- District coordinates for Open-Meteo API
- Model file paths
- API configuration

Edit this if:
- Adding new districts
- Changing model locations
- Modifying API settings

### website/script.js
Contains:
- API_BASE_URL = 'http://localhost:5000' (backend address)
- Chart.js configuration
- UI interaction logic

Edit `API_BASE_URL` if using different port for backend

### backend/requirements.txt
Python dependencies:
- tensorflow, keras (ML framework)
- flask, flask-cors (API)
- pandas, numpy, scikit-learn (data processing)
- requests (API calls)

Install with: `pip install -r requirements.txt`

---

## Performance Tips

1. **First prediction is slower** (model loading) - subsequent predictions are faster
2. **Use diagnostic tool regularly** to verify system health
3. **Keep backend terminal visible** to see error logs
4. **Use browser F12 console** to see client-side debug messages
5. **Check both terminals** - errors might be on backend or frontend

---

## API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check if backend is running |
| `/api/districts` | GET | List available districts |
| `/api/model-info/<district>` | GET | Get model info for district |
| `/api/predict` | POST | Generate 15-day forecast |

### Example API Calls

**1. Health Check**
```bash
curl http://localhost:5000/health
```

**2. Get Districts**
```bash
curl http://localhost:5000/api/districts
```

**3. Get Model Info**
```bash
curl http://localhost:5000/api/model-info/beed
```

**4. Make Prediction**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"district":"beed","date":"2026-03-26"}'
```

---

## Port Reference

| Service | Port | URL |
|---------|------|-----|
| Frontend | 8000 | http://localhost:8000 |
| Backend API | 5000 | http://localhost:5000 |
| Diagnostic | 8000 | http://localhost:8000/diagnostic.html |

---

## Quick Commands

```bash
# Navigate to project
cd c:\Users\ACER\projects\unicef

# Install dependencies
pip install -r backend/requirements.txt

# Train model
cd backend && python train_model.py

# Start backend
cd backend && python app.py

# Start frontend (separate terminal)
cd website && python -m http.server 8000

# Kill Python processes (if stuck)
Get-Process -Name python | Stop-Process -Force

# Check if port is in use
netstat -ano | findstr :5000
netstat -ano | findstr :8000

# Find which process uses a port
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess
```

---

## Still Not Working?

1. **Check diagnostic tool**: http://localhost:8000/diagnostic.html
2. **Check browser console**: F12 → Console tab
3. **Check backend logs**: Look at terminal running `python app.py`
4. **Check frontend logs**: Look at terminal running `python -m http.server`
5. **Try hard refresh**: Ctrl+Shift+Delete then reload
6. **Restart both services**: Stop both processes and restart

---

## Need Help?

Review these files:
1. `SETUP_CHECKLIST.md` - Verify setup is complete
2. Diagnostic tool - http://localhost:8000/diagnostic.html
3. Browser console - F12 → Console tab for error messages
4. Backend terminal - Check for error messages
