# API Documentation

## Prediction Endpoint

### POST `/predict`

Get 15-day temperature forecasts with metrics (actual temperature and RMSE).

**Request:**
```json
{
  "district": "beed",
  "date": "2025-09-11"
}
```

**Parameters:**
- `district` (string, required): District name (case-insensitive)
  - Supported: beed, Jalna, Chhatrapati Sambhajinagar, Dhule, Jalgaon, Wardha, Yavatmal
- `date` (string, required): Base date in YYYY-MM-DD format
  - Predictions start from the next day

**Response (200 OK):**
```json
{
  "predictions": [
    {
      "Day": "Day 01",
      "Date": "2025-09-12",
      "Predicted_Tmax": 31.55
    },
    ...
  ],
  "metrics": [
    {
      "Day": "Day 01",
      "Date": "2025-09-12",
      "Predicted_Tmax": 31.55,
      "Actual_Tmax": 28.5,
      "RMSE": 3.05
    },
    ...
  ]
}
```

**Response Fields:**
- `predictions`: Array of 15 predicted temperatures
  - `Day`: Day label (Day 01 - Day 15)
  - `Date`: Forecast date
  - `Predicted_Tmax`: Predicted maximum temperature in °C

- `metrics`: Array of 15 metric records
  - `Actual_Tmax`: Actual temperature (or "N/A" if not available)
  - `RMSE`: Root Mean Square Error (or "N/A" if actual unavailable)

**Error Responses:**

400 Bad Request - Missing parameters:
```json
{"error": "'district' and 'date' fields are required"}
```

400 Bad Request - Unknown district:
```json
{"error": "Unknown district: xyz"}
```

500 Internal Server Error:
```json
{
  "error": "internal server error",
  "detail": "Error message",
  "trace": "Full Python traceback"
}
```

## Examples

### cURL
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"district":"beed","date":"2025-09-11"}'
```

### Python (requests)
```python
import requests
import datetime

payload = {
    "district": "beed",
    "date": datetime.date.today().isoformat()
}

response = requests.post("http://localhost:5000/predict", json=payload)
print(response.json())
```

### PowerShell
```powershell
$d = (Get-Date).ToString('yyyy-MM-dd')
Invoke-RestMethod -Uri http://localhost:5000/predict `
  -Method Post `
  -ContentType 'application/json' `
  -Body (@{district='beed'; date=$d} | ConvertTo-Json)
```

## Notes

- **Actual Temperatures**: Only available for dates <= 2 days ago
- **Future Forecasts**: Show "N/A" for Actual_Tmax and RMSE
- **Model**: All districts use the Beed-trained model
- **Time Zone**: All times are in Asia/Kolkata timezone
- **Safety Alert**: Temperatures ≥ 41°C are flagged as unsafe for field operations
