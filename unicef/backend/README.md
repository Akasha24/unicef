# Weather Forecast Backend API

A Flask-based REST API for temperature prediction using pre-trained Conv1D-LSTM neural networks trained on meteorological data.

## Quick Start

### Prerequisites
- Python 3.8+
- TensorFlow 2.x
- See `requirements.txt` for full dependencies

### Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the server:**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Health Check
```
GET /health
```

Returns: Service status

### 2. Get Available Districts
```
GET /api/districts
```

### 3. Get Model Information
```
GET /api/model-info/<district>
```

### 4. Single Prediction (POST)
```
POST /api/predict
```

**Request Body:**
```json
{
  "district": "beed",
  "date": "2026-03-26"
}
```

**Response:**
```json
{
  "status": "success",
  "district": "beed",
  "base_date": "2026-03-26",
  "predictions": [
    {"day": 1, "date": "2026-03-27", "tmax": 35.42},
    {"day": 2, "date": "2026-03-28", "tmax": 36.15},
    ...
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"district":"beed","date":"2026-03-26"}'
```

### 5. Batch Prediction (POST)
```
POST /api/predict-batch
```

**Request Body:**
```json
{
  "requests": [
    {"district": "beed", "date": "2026-03-26"},
    {"district": "dhule", "date": "2026-03-26"}
  ]
}
```

## Project Structure

```
backend/
├── app.py                      # Flask application with endpoints
├── models.py                   # Model manager & utilities
├── train_model.py              # Training script
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── {district}_model.keras      # Pre-trained model files
└── {district}_scalers.pkl      # Scaler files (one pair per district)
```

## Training a New Model

```bash
python train_model.py \
  --district beed \
  --csv ./beed_master_2014_2025.csv \
  --epochs 200 \
  --batch_size 32
```

**Arguments:**
- `--district` (required): District name
- `--csv` (required): Path to training CSV file with columns: date, msl, wind_speed, solar_radiation, relative_humidity, rainfall, tmax
- `--epochs` (optional): Training epochs (default: 200)
- `--batch_size` (optional): Batch size (default: 32)

## Model Architecture

- **Input:** 4-day meteorological window × 6 features
- **Layers:** Conv1D (224, 192 filters) → 3× LSTM (64 units) → Dense output (15 days)
- **Loss:** MAE
- **Output:** 15-day temperature forecast

## Error Handling

| Error | Status | Solution |
|-------|--------|----------|
| Model not found | 404 | Run `train_model.py` to train a model |
| Invalid district | 400 | Use `/api/districts` to see available options |
| API unavailable | 503 | Check Open-Meteo API connectivity |
| Missing fields | 400 | Ensure `district` and `date` (YYYY-MM-DD) are provided |

## Performance

- **Single Prediction:** 2-5 seconds (including API calls)
- **Batch (10 requests):** 15-30 seconds
- **Model Inference:** 100-200ms per request

## Production Deployment

```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Dependencies

- Flask 2.x
- TensorFlow 2.x
- pandas, numpy
- scikit-learn
- requests
- flask-cors

See `requirements.txt` for exact versions.

## Notes

- Training is time-consuming; GPU acceleration recommended
- Server caches loaded models in memory
- CORS enabled for all origins
- Predictions fetch live data from Open-Meteo API
