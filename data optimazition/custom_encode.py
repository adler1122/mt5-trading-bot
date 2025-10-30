import pandas as pd
import os

# Inputs
pattern = input("Enter pattern name (e.g., fvg, orderblock): ").lower()
symbol = input("Enter symbol (e.g., xauusd): ").lower()
base_path = f"ml datasets/{symbol}/{pattern}"

# Session encoding map
session_map = {
    "Sydney": 0,
    "Tokyo": 1,
    "London": 2,
    "New York": 3
}

for filename in os.listdir(base_path):
    if not filename.endswith(".csv"):
        continue

    path = os.path.join(base_path, filename)
    df = pd.read_csv(path)

    # Encode boolean-like columns
    for col in df.select_dtypes(include=["bool"]).columns:
        if df[col].dropna().isin([True, False]).all():
            df[col] = df[col].astype(int)

    # Encode session column
    if "session" in df.columns:
        df["session"] = df["session"].astype(str).map(session_map)
    if "entry_session" in df.columns:
        df["entry_session"]=df["entry_session"].astype(str).map(session_map)

    # Save in-place
    df.to_csv(path, index=False)
    print(f"Encoded: {filename}")