import os
import sys
import pickle
import argparse
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

"""
Train a model for a district and save artifacts into this backend folder.
Usage:
    python train_model.py --district beed --csv ./beed_master_2014_2025.csv

This replicates the notebook training logic and writes:
 - beed_model.keras
 - beed_scalers.pkl

Notes:
 - Training may be slow depending on hardware.
 - Ensure dependencies in requirements.txt are installed.
"""

parser = argparse.ArgumentParser()
parser.add_argument("--district", required=True, help="District name, e.g. beed")
parser.add_argument("--csv", required=True, help="Path to district CSV file")
parser.add_argument("--epochs", type=int, default=200)
parser.add_argument("--batch_size", type=int, default=32)
args = parser.parse_args()

district = args.district
csv_path = args.csv
epochs = args.epochs
batch_size = args.batch_size

if not os.path.exists(csv_path):
    print(f"CSV not found: {csv_path}")
    sys.exit(1)

print(f"Training for district: {district}")
print(f"Reading: {csv_path}")

df = pd.read_csv(csv_path)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date').reset_index(drop=True)
df['month'] = df['date'].dt.month

feature_cols = ['msl', 'wind_speed', 'solar_radiation', 'relative_humidity', 'rainfall', 'month']
target_col = 'tmax'

scaler_X = MinMaxScaler()
scaler_y = MinMaxScaler()

df[feature_cols] = scaler_X.fit_transform(df[feature_cols])
df[[target_col]] = scaler_y.fit_transform(df[[target_col]])


def create_sequences(data, target, window=4, horizon=15):
    X, y = [], []
    for i in range(len(data) - window - horizon):
        X.append(data[i:i+window])
        y.append(target[i+window:i+window+horizon])
    return np.array(X), np.array(y)

X_train, y_train = create_sequences(df[feature_cols].values, df[target_col].values, window=4, horizon=15)
print("X_train shape:", X_train.shape)
print("y_train shape:", y_train.shape)

model = Sequential()
model.add(Conv1D(filters=224, kernel_size=1, activation='relu', input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Conv1D(filters=192, kernel_size=1, activation='relu'))
model.add(Dropout(0.30))
model.add(LSTM(64, return_sequences=True))
model.add(LSTM(64, return_sequences=True))
model.add(LSTM(64))
model.add(Dropout(0.10))
model.add(Dense(15))

model.compile(optimizer=Adam(learning_rate=1e-4), loss='mae')
model.summary()

model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.1, verbose=1)

# save into backend folder
safe_name = district.lower().replace(' ', '_')
backend_dir = os.path.dirname(__file__)
model_path = os.path.join(backend_dir, f"{safe_name}_model.keras")
scalers_path = os.path.join(backend_dir, f"{safe_name}_scalers.pkl")

print(f"Saving model to: {model_path}")
model.save(model_path)

print(f"Saving scalers to: {scalers_path}")
with open(scalers_path, 'wb') as f:
    pickle.dump({'scaler_X': scaler_X, 'scaler_y': scaler_y}, f)

print("Done.")
