"""
Model management and prediction utilities for weather forecasting.
Handles loading pre-trained models, scalers, and generating predictions.
"""

import os
import pickle
import numpy as np
import pandas as pd
import requests
from datetime import datetime, timedelta, date
from pathlib import Path
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_squared_error

# Get the directory of this script
BACKEND_DIR = Path(__file__).parent


class ModelManager:
    """Manages loading and prediction with trained models."""
    
    DISTRICT_COORDS = {
        "beed": {"lat": 18.9901, "lon": 75.7531},
        "Chhatrapati Sambhajinagar": {"lat": 19.8762, "lon": 75.3433},
        "Dhule": {"lat": 20.9042, "lon": 74.7749},
        "Jalgaon": {"lat": 21.0077, "lon": 75.5626},
        "Jalna": {"lat": 19.8410, "lon": 75.8864},
        "Wardha": {"lat": 20.7453, "lon": 78.6022},
        "Yavatmal": {"lat": 20.3899, "lon": 78.1307},
    }
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
    
    def get_safe_name(self, district):
        """Convert district name to safe filename format."""
        return district.lower().replace(" ", "_")
    
    def load_model_and_scalers(self, district):
        """Load model and scalers for a district."""
        safe_name = self.get_safe_name(district)
        
        if safe_name in self.models:
            return self.models[safe_name], self.scalers[safe_name]
        
        model_path = BACKEND_DIR / f"{safe_name}_model.keras"
        scalers_path = BACKEND_DIR / f"{safe_name}_scalers.pkl"
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
        if not scalers_path.exists():
            raise FileNotFoundError(f"Scalers not found: {scalers_path}")
        
        model = load_model(str(model_path))
        with open(str(scalers_path), 'rb') as f:
            scalers = pickle.load(f)
        
        self.models[safe_name] = model
        self.scalers[safe_name] = scalers
        
        return model, scalers
    
    def validate_district(self, district_input):
        """Validate and normalize district name."""
        for key in self.DISTRICT_COORDS:
            if key.lower() == district_input.lower():
                return key
        raise ValueError(
            f"District '{district_input}' not found. "
            f"Available: {', '.join(self.DISTRICT_COORDS.keys())}"
        )
    
    def fetch_meteorological_data(self, date_str, district):
        """
        Fetch meteorological data from Open-Meteo API.
        Units are converted to match ERA5 training data.
        """
        lat = self.DISTRICT_COORDS[district]["lat"]
        lon = self.DISTRICT_COORDS[district]["lon"]
        
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_date = target_date - timedelta(days=4)
        end_date = target_date
        today_real = date.today()
        
        if end_date < today_real - timedelta(days=2):
            base_url = "https://archive-api.open-meteo.com/v1/archive"
        else:
            base_url = "https://api.open-meteo.com/v1/forecast"
        
        url = (
            f"{base_url}?"
            f"latitude={lat}&longitude={lon}"
            f"&hourly=relativehumidity_2m,pressure_msl,windspeed_10m,"
            f"shortwave_radiation,precipitation"
            f"&start_date={start_date}&end_date={end_date}"
            f"&timezone=Asia/Kolkata"
        )
        
        # Retry logic
        for attempt in range(3):
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                break
            except Exception as e:
                if attempt == 2:
                    raise Exception(f"Failed to fetch data after 3 attempts: {e}")
        
        data = response.json()
        hourly = pd.DataFrame(data["hourly"])
        hourly["time"] = pd.to_datetime(hourly["time"])
        hourly["date"] = hourly["time"].dt.date
        
        daily = hourly.groupby("date").agg({
            "relativehumidity_2m": "mean",
            "pressure_msl": "mean",
            "windspeed_10m": "mean",
            "shortwave_radiation": "sum",
            "precipitation": "sum",
        }).reset_index()
        
        # Unit conversions to match ERA5 training data
        daily["pressure_msl"] = daily["pressure_msl"] * 100  # hPa → Pa
        daily["windspeed_10m"] = daily["windspeed_10m"] / 3.6  # km/h → m/s
        daily["shortwave_radiation"] = daily["shortwave_radiation"] * 3600  # W/m² → J/m²
        daily["month"] = pd.to_datetime(daily["date"]).dt.month
        
        daily = daily.rename(columns={
            "pressure_msl": "msl",
            "windspeed_10m": "wind_speed",
            "shortwave_radiation": "solar_radiation",
            "relativehumidity_2m": "relative_humidity",
            "precipitation": "rainfall",
        })
        
        daily = daily[["date", "msl", "wind_speed", "solar_radiation",
                       "relative_humidity", "rainfall", "month"]]
        
        daily = daily.fillna(method="ffill").fillna(method="bfill")
        daily["date"] = pd.to_datetime(daily["date"])
        daily = daily.set_index("date")
        
        return daily
    
    def fetch_actual_tmax(self, date_str, district):
        """Fetch actual Tmax (°C) from Open-Meteo API."""
        lat = self.DISTRICT_COORDS[district]["lat"]
        lon = self.DISTRICT_COORDS[district]["lon"]
        
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        start_date = target_date - timedelta(days=4)
        end_date = target_date
        today_real = date.today()
        
        if end_date < today_real - timedelta(days=2):
            base_url = "https://archive-api.open-meteo.com/v1/archive"
        else:
            base_url = "https://api.open-meteo.com/v1/forecast"
        
        url = (
            f"{base_url}?"
            f"latitude={lat}&longitude={lon}"
            f"&hourly=temperature_2m"
            f"&start_date={start_date}&end_date={end_date}"
            f"&timezone=Asia/Kolkata"
        )
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            hourly = pd.DataFrame(data["hourly"])
            hourly["time"] = pd.to_datetime(hourly["time"])
            hourly["date"] = hourly["time"].dt.date
            
            daily = hourly.groupby("date").agg({"temperature_2m": "max"}).reset_index()
            daily["date"] = pd.to_datetime(daily["date"])
            daily = daily.set_index("date")
            daily = daily.ffill().bfill()
            
            return float(daily["temperature_2m"].iloc[-1])
        except Exception as e:
            return None
    
    def predict(self, date_str, district):
        """
        Generate 15-day temperature forecast.
        
        Returns:
            dict: Contains predictions, dates, and metadata
        """
        # Validate and normalize district
        district = self.validate_district(district)
        district_key = self.get_safe_name(district)
        
        # Load model and scalers
        model, scalers = self.load_model_and_scalers(district)
        scaler_X = scalers["scaler_X"]
        scaler_y = scalers["scaler_y"]
        
        # Fetch meteorological data
        df = self.fetch_meteorological_data(date_str, district)
        df = df.sort_values("date")
        
        # Prepare features
        features = df[["msl", "wind_speed", "solar_radiation",
                       "relative_humidity", "rainfall", "month"]]
        last_4_days = features.head(4)
        scaled = scaler_X.transform(last_4_days)
        X_input = np.expand_dims(scaled, axis=0)  # shape (1, 4, 6)
        
        # Generate prediction
        pred_scaled = model.predict(X_input, verbose=0)
        pred_tmax = scaler_y.inverse_transform(pred_scaled)[0]
        
        # Prepare results
        base_date = pd.to_datetime(date_str)
        future_dates = [base_date + pd.Timedelta(days=i+1) for i in range(15)]
        
        predictions = []
        for i in range(15):
            predictions.append({
                "day": i + 1,
                "date": future_dates[i].strftime("%Y-%m-%d"),
                "tmax": round(float(pred_tmax[i]), 2),
            })
        
        return {
            "district": district,
            "base_date": date_str,
            "predictions": predictions,
            "status": "success"
        }
    
    def get_available_districts(self):
        """Return list of available districts."""
        return list(self.DISTRICT_COORDS.keys())
    
    def get_model_info(self, district):
        """Get metadata about a trained model."""
        try:
            district = self.validate_district(district)
            safe_name = self.get_safe_name(district)
            
            model_path = BACKEND_DIR / f"{safe_name}_model.keras"
            scalers_path = BACKEND_DIR / f"{safe_name}_scalers.pkl"
            
            return {
                "district": district,
                "model_exists": model_path.exists(),
                "scalers_exist": scalers_path.exists(),
                "model_size_mb": model_path.stat().st_size / (1024*1024) if model_path.exists() else 0,
            }
        except Exception as e:
            return {"error": str(e)}
