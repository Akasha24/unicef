# 15-Day Temperature Forecast System

UNICEF machine learning system to predict maximum temperatures for 15 days ahead using Conv1D + LSTM neural network. Helps agricultural planning and identifies unsafe temperature conditions (Tmax ≥ 41°C).

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/Akasha24/unicef.git
cd unicef
```

### 2. Setup Python Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1        # Windows PowerShell
# or
.venv\Scripts\activate.bat         # Windows CMD
# or
source .venv/bin/activate          # macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r website/backend/requirements.txt
```

### 4. Run the Application

```bash
python run.py
```

### 5. Open in Browser

```
http://localhost:5000
```

That's it! 🎉 The app is ready to use.

---

## 📁 Project Structure

```
unicef/
├── src/                           # Source code
│   ├── api/                       # Flask API
│   │   ├── __init__.py
│   │   └── app.py                # Flask server
│   ├── ml/                        # ML pipeline
│   │   ├── __init__.py
│   │   └── pipeline.py            # Training & prediction logic
│   └── frontend/                  # Web UI
│       ├── __init__.py
│       └── static/
│           ├── index.html
│           ├── app.js
│           └── styles.css
├── data/                          # Training datasets
│   └── beed_master_2015_2024.csv
├── models/                        # Trained models
│   └── beed_model.keras
├── scalers/                       # ML scalers (in repo!)
│   └── beed_scalers.pkl
├── scripts/                       # CLI scripts
│   └── test_predict.py
├── docs/                          # Documentation
│   └── API.md
├── website/                       # Old structure (for reference)
├── requirements.txt               # Dependencies
├── run.py                         # Main entry point
└── README.md                      # This file
```

---

## ✨ Features

- ✅ **15-day forecasts** using trained ML model
- ✅ **Real-time weather data** from Open-Meteo API (no API key needed)
- ✅ **Actual vs Predicted** comparison with RMSE metrics
- ✅ **Safety alerts** for dangerous temperatures (Tmax ≥ 41°C)
- ✅ **Beautiful UI** with interactive charts and tables
- ✅ **Multiple districts** - Beed, Jalna, Wardha, Dhule, Jalgaon, and more

---

## 🌍 Supported Districts

- Beed
- Chhatrapati Sambhajinagar
- Dhule
- Jalgaon
- Jalna
- Wardha
- Yavatmal

*(All districts use the Beed-trained model)*

---

## 📊 How to Use

### Web Interface

1. Open http://localhost:5000
2. Select a **District**
3. Select a **Base Date**
4. Click **"Get Forecast"**
5. View 15-day predictions with actual temperatures and RMSE

### API Endpoint

**POST** to `/predict`:

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"district":"beed","date":"2025-09-11"}'
```

See [docs/API.md](docs/API.md) for full API documentation.

### CLI Testing

```bash
# Test prediction from command line
python scripts/test_predict.py beed 2025-09-11

# Using Python directly
python -m src.ml.pipeline predict --district beed --date 2025-09-11
```

---

## 🤖 Model Architecture

- **Type:** Conv1D + LSTM (3-layer LSTM)
- **Input:** 4 days of 6 weather features
- **Output:** 15-day temperature forecasts
- **Training Data:** Beed district (2015-2024, daily)

**Features:**
- Mean Sea Level Pressure
- Wind Speed
- Solar Radiation
- Relative Humidity
- Rainfall
- Month (seasonal marker)

---

## ⚠️ Troubleshooting

### Port 5000 already in use

**PowerShell:**
```powershell
$proc = Get-Process python | Where-Object {(netstat -ano | findstr ":5000").Split()[-1] -eq $_.Id}
Stop-Process -Id $proc.Id -Force
```

Then restart: `python run.py`

### Module import errors

If you see `ModuleNotFoundError`, ensure:
1. Virtual environment is activated
2. All dependencies installed: `pip install -r website/backend/requirements.txt`
3. Running from project root directory

### Missing model/scaler files

Models and scalers are in the repository:
- `models/beed_model.keras`
- `scalers/beed_scalers.pkl`

If missing, run:
```bash
python -m src.ml.pipeline train --districts beed
```

### No actual temperature data (shows "N/A")

- Actual data only available for dates **≤ 2 days ago**
- Future forecasts won't have actual temperatures (this is expected)
- If API fails, system uses synthetic data

---

## 📦 Requirements

- Python 3.8+
- TensorFlow 2.8+
- Flask 2.0+
- pandas, numpy, scikit-learn
- requests, flask-cors

See [website/backend/requirements.txt](website/backend/requirements.txt) for all dependencies.

---

## 🎯 Performance

- **Prediction time:** ~500ms
- **Model size:** ~10MB
- **Memory:** ~300MB (model loading)
- **API response:** ~2-3 seconds (includes weather API call)

---

## 📝 Notes

- All districts use **Beed model** (trained on Beed data 2015-2024)
- RMSE estimates model accuracy (lower is better)
- Safety threshold: **Tmax ≥ 41°C** flagged as unsafe for field operations
- Weather data from [Open-Meteo](https://open-meteo.com/) (free, no key required)
- All times in **Asia/Kolkata** timezone

---

## 🔧 Training a New Model

```bash
# Requires CSV file in data/ folder
python -m src.ml.pipeline train --districts beed
```

Saves to:
- `models/beed_model.keras`
- `scalers/beed_scalers.pkl`

---

## 📚 Documentation

- [API Documentation](docs/API.md) - Complete API reference
- Training data format documented in code comments

---

## 👥 Support

Check the Flask server logs for detailed error messages:
```
ERROR messages show prediction failures
WARNING messages show API/data fetch issues
```

---

## 📄 License

UNICEF Project
