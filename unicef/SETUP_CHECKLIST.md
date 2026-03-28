# Quick Start Checklist

Use this checklist to verify your system is properly configured and running.

## ✓ Prerequisites

- [ ] Python 3.8+ installed (`python --version`)
- [ ] Project folder exists: `c:\Users\ACER\projects\unicef\`
- [ ] Virtual environment created (if using one)
- [ ] Dependencies installed from `requirements.txt`

## ✓ Backend Setup

- [ ] Backend folder exists: `backend/`
- [ ] `app.py` present in backend folder
- [ ] `models.py` present in backend folder
- [ ] `config.py` present in backend folder
- [ ] All model files (.keras files) exist in backend folder
- [ ] All scaler files (.pkl files) exist in backend folder

### Start Backend

```bash
cd backend
python app.py
```

**Expected output in terminal:**
```
* Running on http://127.0.0.1:5000
* WARNING: This is a development server. Do not use it in production.
```

- [ ] Backend started successfully
- [ ] Check health: Open http://localhost:5000/health in browser
- [ ] You should see: `{"status":"healthy","service":"weather-forecast-api","version":"1.0.0"}`

## ✓ Frontend Setup

- [ ] Website folder exists: `website/`
- [ ] `index.html` present in website folder
- [ ] `style.css` present in website folder
- [ ] `script.js` present in website folder
- [ ] `diagnostic.html` present in website folder (for troubleshooting)

### Start Frontend (in separate terminal)

```bash
cd website
python -m http.server 8000
```

**Expected output in terminal:**
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/)
```

- [ ] Frontend started successfully
- [ ] Check frontend: Open http://localhost:8000 in browser
- [ ] You should see the Weather Forecast application UI

## ✓ Connectivity Test

- [ ] Both servers running (backend on 5000, frontend on 8000)
- [ ] Open browser to http://localhost:8000/diagnostic.html
- [ ] Run all diagnostic checks
- [ ] All checks should show ✓ (green checkmarks)

**Key diagnostic checks:**
- [ ] Frontend page loads
- [ ] JavaScript dependencies loaded
- [ ] Backend health check passes (/health endpoint)
- [ ] Districts API works (/api/districts endpoint)
- [ ] Model info API works (/api/model-info/beed endpoint)
- [ ] Model files exist and readable

## ✓ Functionality Test

- [ ] Open http://localhost:8000 in browser
- [ ] Select a district from the dropdown (should show available districts)
- [ ] Select a date from the calendar
- [ ] Click "Get Forecast" button
- [ ] Wait for results (should show 15-day forecast)
- [ ] Check results display:
  - [ ] Summary statistics (Min/Max/Average temperature)
  - [ ] 15 day forecast cards
  - [ ] Temperature chart
  - [ ] Export to CSV option

## ✓ Troubleshooting

If you encounter issues:

1. **"Fetch failed: TypeError: Failed to fetch"**
   - Backend not running or wrong port
   - Solution: Start backend with `python app.py` in backend folder
   - Verify it shows running on http://127.0.0.1:5000

2. **"Cannot find module..."**
   - Missing dependencies
   - Solution: Run `pip install -r requirements.txt`

3. **"404 Not Found" for model files**
   - Model files not found
   - Solution: Make sure all .keras and .pkl files are in backend folder
   - Run `python train_model.py` to regenerate

4. **Port already in use**
   - Another application using the port
   - Solution: Kill process or change port in script.js (for frontend) or app.py (for backend)

5. **CORS error in browser console**
   - Backend CORS not configured correctly
   - Solution: Ensure `from flask_cors import CORS` and `CORS(app)` in app.py

## ✓ Files Checklist

```
unicef/
├── backend/
│   ├── app.py                 ✓ Flask API server
│   ├── models.py              ✓ Model management logic
│   ├── config.py              ✓ Configuration
│   ├── train_model.py         ✓ Model training script
│   ├── requirements.txt        ✓ Dependencies
│   ├── weather_model_beed.keras      ✓ Trained model
│   ├── weather_scaler_beed.pkl       ✓ Data scaler
│   └── [other model files...]        ✓ More models
│
├── website/
│   ├── index.html             ✓ Main application
│   ├── style.css              ✓ Styling
│   ├── script.js              ✓ JavaScript logic
│   └── diagnostic.html        ✓ Diagnostic tool
│
├── readme.md                  ✓ Project documentation
└── START_SERVERS.ps1          ✓ Startup script
```

## ✓ Next Steps After Successful Startup

1. Explore the diagnostic tool at http://localhost:8000/diagnostic.html
2. Make a forecast by selecting a district and date
3. Export results to CSV
4. View the temperature trend chart
5. Try different districts and dates

---

**Status: Ready to Use** ✅

If all checkboxes above are checked, your system is ready!
