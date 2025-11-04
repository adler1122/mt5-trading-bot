import pandas as pd

# --- Timeframes and file paths ---
timeframes = ["M15", "M30", "H1", "H4", "D1"]
symbol = input("Enter symbol: ")
files = {tf: f"datasets/{symbol}_{tf}.csv" for tf in timeframes}

# --- Load all datasets ---
datasets = {}
for tf in timeframes:
    df = pd.read_csv(files[tf])
    df['time'] = pd.to_datetime(df['time'])  # Convert to datetime
    df.drop(columns=["spread", "real_volume"], inplace=True)
    datasets[tf] = df

# --- Detect noisy days from D1 based on volume only ---
daily_df = datasets["D1"].copy()

def get_upper_volume_threshold(series):
    q3 = series.quantile(0.75)
    iqr = q3 - series.quantile(0.25)
    return q3 + 1.5 * iqr

vol_threshold = get_upper_volume_threshold(daily_df["tick_volume"])

# Mark noisy days: volume > upper threshold
noisy_dates = set(daily_df.loc[daily_df["tick_volume"] > vol_threshold, "time"].dt.date)

# --- Clean and save intra-day timeframes ---
for tf in ["M15", "M30", "H1", "H4"]:
    df = datasets[tf]
    df["date"] = df["time"].dt.date
    df["time_only"] = df["time"].dt.time
    df["noisy_day"] = df["date"].isin(noisy_dates)
    df.drop(columns=["time"], inplace=True)
    df.to_csv(f"cleaned_{symbol}_{tf}.csv", index=False)