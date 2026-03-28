from __future__ import annotations
import argparse
import os
import pickle
from datetime import date, datetime, timedelta
from typing import Dict, Optional
import numpy as np
import pandas as pd
import requests
from sklearn.metrics import mean_squared_error
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model
import logging

logger = logging.getLogger(__name__)
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UNICEF_DIR = os.path.join(REPO_ROOT, "unicef")
ML_MODEL_DIR = os.path.join(UNICEF_DIR, "ml model")
MODEL_DIR_DEFAULT = os.path.join(UNICEF_DIR, "models")
SCALER_DIR_DEFAULT = os.path.join(UNICEF_DIR, "scalers")
DISTRICT_COORDS: Dict[str, Dict[str, float]] = {
    "beed": {"lat": 18.9901, "lon": 75.7531},
    "Chhatrapati Sambhajinagar": {"lat": 19.8762, "lon": 75.3433},
    "Dhule": {"lat": 20.9042, "lon": 74.7749},
    "Jalgaon": {"lat": 21.0077, "lon": 75.5626},
    "Jalna": {"lat": 19.8410, "lon": 75.8864},
    "Wardha": {"lat": 20.7453, "lon": 78.6022},
    "Yavatmal": {"lat": 20.3899, "lon": 78.1307},
}


def _lookup_district_key(name: str) -> Optional[str]:
    """Return canonical district key from a case-insensitive name."""
    for key in DISTRICT_COORDS:
        if key.lower() == name.strip().lower():
            return key
    return None


def fetch_paper_style_inputs(date_str: str, district: str) -> pd.DataFrame:
    """Fetch meteorological inputs for `district` and return daily features.

    Unit conversions are applied to match ERA5 training units.
    """
    lat = DISTRICT_COORDS[district]["lat"]
    lon = DISTRICT_COORDS[district]["lon"]

    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    start_date = target_date - timedelta(days=4)
    end_date = target_date
    today_real = date.today()

    base_url = (
        "https://archive-api.open-meteo.com/v1/archive"
        if end_date < today_real - timedelta(days=2)
        else "https://api.open-meteo.com/v1/forecast"
    )

    url = (
        f"{base_url}?latitude={lat}&longitude={lon}"
        f"&hourly=relativehumidity_2m,pressure_msl,windspeed_10m,"
        f"shortwave_radiation,precipitation&start_date={start_date}&end_date={end_date}"
        f"&timezone=Asia/Kolkata"
    )

    for attempt in range(3):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            break
        except Exception as exc:
            logger.warning("Fetch attempt %d failed: %s", attempt + 1, exc)
            if attempt == 2:
                raise

    hourly = pd.DataFrame(data["hourly"])  # may raise KeyError if API changed
    hourly["time"] = pd.to_datetime(hourly["time"])
    hourly["date"] = hourly["time"].dt.date

    daily = (
        hourly.groupby("date")
        .agg(
            relativehumidity_2m=("relativehumidity_2m", "mean"),
            pressure_msl=("pressure_msl", "mean"),
            windspeed_10m=("windspeed_10m", "mean"),
            shortwave_radiation=("shortwave_radiation", "sum"),
            precipitation=("precipitation", "sum"),
        )
        .reset_index()
    )

    daily["pressure_msl"] = daily["pressure_msl"] * 100  # hPa -> Pa
    daily["windspeed_10m"] = daily["windspeed_10m"] / 3.6  # km/h -> m/s
    daily["shortwave_radiation"] = daily["shortwave_radiation"] * 3600  # W/m2 -> J/m2

    daily["month"] = pd.to_datetime(daily["date"]).dt.month

    daily = daily.rename(
        columns={
            "pressure_msl": "msl",
            "windspeed_10m": "wind_speed",
            "shortwave_radiation": "solar_radiation",
            "relativehumidity_2m": "relative_humidity",
            "precipitation": "rainfall",
        }
    )

    daily = daily[
        [
            "date",
            "msl",
            "wind_speed",
            "solar_radiation",
            "relative_humidity",
            "rainfall",
            "month",
        ]
    ]
    daily = daily.ffill().bfill()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.set_index("date")
    return daily


def fetch_tmax(date_str: str, district: str) -> Optional[float]:
    """Fetch maximum temperature for a date/district. Returns None if unavailable."""
    lat = DISTRICT_COORDS[district]["lat"]
    lon = DISTRICT_COORDS[district]["lon"]

    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    start_date = target_date - timedelta(days=4)
    end_date = target_date
    today_real = date.today()

    base_url = (
        "https://archive-api.open-meteo.com/v1/archive"
        if end_date < today_real - timedelta(days=2)
        else "https://api.open-meteo.com/v1/forecast"
    )

    url = f"{base_url}?latitude={lat}&longitude={lon}&hourly=temperature_2m&start_date={start_date}&end_date={end_date}&timezone=Asia/Kolkata"

    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()

    hourly = pd.DataFrame(data["hourly"])
    hourly["time"] = pd.to_datetime(hourly["time"])
    hourly["date"] = hourly["time"].dt.date

    daily = hourly.groupby("date").agg({"temperature_2m": "max"}).reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.set_index("date")
    daily = daily.ffill().bfill()

    try:
        return float(daily["temperature_2m"].iloc[-1])
    except Exception:
        return None


def train_for_district(
    district: str, *, model_dir: Optional[str] = None, scaler_dir: Optional[str] = None
) -> None:
    """Train and persist model + scalers for a district.

    NOTE: This function mirrors the original training architecture but is
    intentionally explicit about outputs and directories.
    """

    logger.info("Training model for %s", district)
    safe_name = district.lower().replace(" ", "_")

    model_dir = model_dir or MODEL_DIR_DEFAULT
    scaler_dir = scaler_dir or SCALER_DIR_DEFAULT

    csv_dir = ML_MODEL_DIR

    candidates = [
        os.path.join(csv_dir, f"{district}_master_2015_2025.csv"),
        os.path.join(csv_dir, f"{district}_master_2015_2024.csv"),
        os.path.join(csv_dir, f"{safe_name}_master_2015_2025.csv"),
        os.path.join(csv_dir, f"{safe_name}_master_2015_2024.csv"),
    ]

    csv_path = None
    for c in candidates:
        if os.path.exists(c):
            csv_path = c
            break

    if csv_path is None:
        logger.error(
            "No master CSV found for district %s. Checked: %s", district, candidates
        )
        raise FileNotFoundError(
            f"No master CSV found for district {district}. Checked: {candidates}"
        )

    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    df["month"] = df["date"].dt.month

    feature_cols = [
        "msl",
        "wind_speed",
        "solar_radiation",
        "relative_humidity",
        "rainfall",
        "month",
    ]
    target_col = "tmax"

    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()

    df[feature_cols] = scaler_X.fit_transform(df[feature_cols])
    df[[target_col]] = scaler_y.fit_transform(df[[target_col]])

    def create_sequences(data, target, window=4, horizon=15):
        X, y = [], []
        for i in range(len(data) - window - horizon):
            X.append(data[i : i + window])
            y.append(target[i + window : i + window + horizon])
        return np.array(X), np.array(y)

    X_train, y_train = create_sequences(
        df[feature_cols].values, df[target_col].values, window=4, horizon=15
    )
    logger.info("X_train shape: %s, y_train shape: %s", X_train.shape, y_train.shape)

    model = Sequential()
    model.add(
        Conv1D(
            filters=224,
            kernel_size=1,
            activation="relu",
            input_shape=(X_train.shape[1], X_train.shape[2]),
        )
    )
    model.add(Conv1D(filters=192, kernel_size=1, activation="relu"))
    model.add(Dropout(0.30))
    model.add(LSTM(64, return_sequences=True))
    model.add(LSTM(64, return_sequences=True))
    model.add(LSTM(64))
    model.add(Dropout(0.10))
    model.add(Dense(15))

    model.compile(optimizer=Adam(learning_rate=0.0001), loss="mae")

    model.fit(
        X_train, y_train, epochs=200, batch_size=32, validation_split=0.1, verbose=1
    )

    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(scaler_dir, exist_ok=True)

    model.save(os.path.join(model_dir, f"{safe_name}_model.keras"))
    with open(os.path.join(scaler_dir, f"{safe_name}_scalers.pkl"), "wb") as f:
        pickle.dump({"scaler_X": scaler_X, "scaler_y": scaler_y}, f)


def predict_for_district(
    district_name: str,
    date_input: str,
    *,
    model_dir: Optional[str] = None,
    scaler_dir: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load model/scalers and return predictions + RMSE table (where available).

    Returns the RMSE DataFrame (may contain 'N/A' where actuals are missing).
    """

    district_key = _lookup_district_key(district_name)
    if not district_key:
        raise ValueError(
            f"District '{district_name}' not found. Available: {list(DISTRICT_COORDS.keys())}"
        )

    model_dir = model_dir or MODEL_DIR_DEFAULT
    scaler_dir = scaler_dir or SCALER_DIR_DEFAULT

    safe_name = district_key.lower().replace(" ", "_")
    model_path = os.path.join(model_dir, f"{safe_name}_model.keras")
    scaler_path = os.path.join(scaler_dir, f"{safe_name}_scalers.pkl")
    logger.info("Loading model from %s", model_path)

    # Validate model and scaler files exist before attempting to load them
    if not os.path.exists(model_path):
        msg = (
            f"Model file not found: {model_path}. "
            "Train the model first (see `train_for_district`) or point to the correct model path."
        )
        logger.error(msg)
        raise FileNotFoundError(msg)

    if not os.path.exists(scaler_path):
        msg = (
            f"Scaler file not found: {scaler_path}. "
            "Ensure scalers are present in the scalers directory or re-run training."
        )
        logger.error(msg)
        raise FileNotFoundError(msg)

    try:
        model = load_model(model_path)
    except Exception as exc:
        logger.exception("Failed to load model from %s: %s", model_path, exc)
        raise
    with open(scaler_path, "rb") as f:
        scalers = pickle.load(f)

    scaler_X = scalers["scaler_X"]
    scaler_y = scalers["scaler_y"]

    df = fetch_paper_style_inputs(date_input, district_key)
    df = df.sort_values("date")

    features = df[
        [
            "msl",
            "wind_speed",
            "solar_radiation",
            "relative_humidity",
            "rainfall",
            "month",
        ]
    ]
    last_4_days = features.tail(4)  # use the most recent 4 days
    if len(last_4_days) < 4:
        raise ValueError("Not enough input days to form model input (need 4 days)")

    scaled = scaler_X.transform(last_4_days)
    X_input = np.expand_dims(scaled, axis=0)  # shape (1, 4, 6)

    pred_scaled = model.predict(X_input)
    pred_tmax = scaler_y.inverse_transform(pred_scaled)[0]

    base_date = pd.to_datetime(date_input)
    future_dates = [base_date + pd.Timedelta(days=i + 1) for i in range(15)]

    results_df = pd.DataFrame(
        {
            "Day": [f"Day {i + 1:02d}" for i in range(15)],
            "Date": [d.strftime("%Y-%m-%d") for d in future_dates],
            "Predicted_Tmax": [round(float(t), 2) for t in pred_tmax],
        }
    )

    logger.info("15-Day Tmax Forecast for %s starting %s", district_key, date_input)
    logger.info("%s", results_df.to_string(index=False))

    # compute RMSE where actuals exist
    pred_horizon = [[] for _ in range(15)]
    actual_horizon = [[] for _ in range(15)]

    for i in range(15):
        target_date = base_date + pd.Timedelta(days=i + 1)
        target_str = target_date.strftime("%Y-%m-%d")
        try:
            actual = fetch_tmax(target_str, district_key)
            if actual is None:
                logger.debug("Day %s: actual Tmax not available", i + 1)
                continue
            actual = float(actual)
        except Exception as exc:
            logger.warning("Day %s: fetch failed — %s", i + 1, exc)
            continue

        pred_horizon[i].append(float(np.squeeze(pred_tmax[i])))
        actual_horizon[i].append(actual)

    rmse_rows = []
    for i in range(15):
        pred_val = round(float(pred_tmax[i]), 2)
        if len(actual_horizon[i]) == 0:
            rmse_rows.append(
                {
                    "Day": f"Day {i + 1:02d}",
                    "Date": future_dates[i].strftime("%Y-%m-%d"),
                    "Predicted_Tmax": pred_val,
                    "Actual_Tmax": "N/A",
                    "RMSE": "N/A",
                }
            )
        else:
            rmse = round(
                np.sqrt(mean_squared_error(actual_horizon[i], pred_horizon[i])), 2
            )
            rmse_rows.append(
                {
                    "Day": f"Day {i + 1:02d}",
                    "Date": future_dates[i].strftime("%Y-%m-%d"),
                    "Predicted_Tmax": pred_val,
                    "Actual_Tmax": round(actual_horizon[i][0], 2),
                    "RMSE": rmse,
                }
            )

    rmse_df = pd.DataFrame(rmse_rows)
    logger.info("Horizon-wise RMSE:\n%s", rmse_df.to_string(index=False))
    return results_df, rmse_df


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Train models or run predictions")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_train = sub.add_parser("train", help="Train models for districts")
    p_train.add_argument(
        "--districts",
        nargs="*",
        default=["beed"],
        help="District names to train (default: beed)",
    )

    p_pred = sub.add_parser("predict", help="Run prediction for a district and date")
    p_pred.add_argument(
        "--district", required=True, help="District name (case-insensitive)"
    )
    p_pred.add_argument(
        "--date", required=True, help="Base date for prediction (YYYY-MM-DD)"
    )

    return parser


def main(argv: Optional[list[str]] = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.cmd == "train":
        for d in args.districts:
            key = _lookup_district_key(d)
            if not key:
                logger.error("Unknown district: %s", d)
                continue
            train_for_district(key)

    elif args.cmd == "predict":
        try:
            _ = pd.to_datetime(args.date, format="%Y-%m-%d")
        except Exception:
            logger.error("Invalid date format: %s. Expected YYYY-MM-DD", args.date)
            return

        try:
            predict_for_district(args.district, args.date)
        except Exception as exc:
            logger.exception("Prediction failed: %s", exc)


if __name__ == "__main__":
    main()