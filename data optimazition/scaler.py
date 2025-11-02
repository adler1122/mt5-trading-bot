import pandas as pd
import os
from sklearn.preprocessing import MinMaxScaler
import joblib

# Inputs
pattern = input("Enter pattern name (e.g., fvg, orderblock): ").lower()
symbol = input("Enter symbol (e.g., xauusd): ").lower()
base_path = f"ml datasets/{symbol}/{pattern}"
scaler_folder = "scalers"
os.makedirs(scaler_folder, exist_ok=True)

# Columns to scale by name
scale_cols = ["gap_size", "candle_size", "volume","percentage"]
market_movement_patterns = ["orderblock", "engulfing", "star", "threeinside", "tweezer"]
if pattern in market_movement_patterns:
    scale_cols.append("target")
for filename in os.listdir(base_path):
    if not filename.endswith(".csv"):
        continue

    path = os.path.join(base_path, filename)
    df = pd.read_csv(path)

    # Extract direction and timeframe from filename
    parts = filename.replace(".csv", "").split("_")
    if len(parts) < 4:
        print(f"Skipping malformed filename: {filename}")
        continue
    direction = parts[1]
    timeframe = parts[-1]

    # Select only the columns we want to scale
    cols_to_scale = [col for col in df.columns if col in scale_cols]

    if not cols_to_scale:
        print(f"No matching columns to scale in {filename}")
        continue

    # Fit and apply scaler
    scaler = MinMaxScaler()
    df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])

    # Save scaler
    scaler_name = f"scaler_{symbol}_{pattern}_{direction}_{timeframe}.pkl"
    joblib.dump(scaler, os.path.join(scaler_folder, scaler_name))

    # Save scaled dataset
    df.to_csv(path, index=False)
    print(f"Scaled: {filename} → Saved scaler: {scaler_name}")