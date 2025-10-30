import pandas as pd

# --- Timeframes and file paths ---
timeframes = ["M15", "M30", "H1", "H4", "D1"]
symbol = input("Enter symbol: ")
files = {tf: f"{symbol}_{tf}.csv" for tf in timeframes}

# --- Load all datasets ---
datasets = {}
for tf in timeframes:
    df = pd.read_csv(files[tf])
    df['time'] = pd.to_datetime(df['time'])  # Convert to datetime
    df.drop(columns=["spread", "real_volume"], inplace=True)
    datasets[tf] = df

# --- Detect noisy days from D1 ---
daily_df = datasets["D1"].copy()
daily_df["candle_size"] = daily_df["high"] - daily_df["low"]

def get_iqr_bounds(series):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    return q1 - 1.5 * iqr, q3 + 1.5 * iqr

size_low, size_high = get_iqr_bounds(daily_df["candle_size"])
vol_low, vol_high = get_iqr_bounds(daily_df["tick_volume"])

noisy_dates = set(daily_df.loc[
    (daily_df["candle_size"] < size_low) | (daily_df["candle_size"] > size_high) |
    (daily_df["tick_volume"] < vol_low) | (daily_df["tick_volume"] > vol_high),"time"].dt.date)

# --- Clean and save intra-day timeframes ---
for tf in ["M15", "M30", "H1", "H4"]:
    df = datasets[tf]
    df["date"] = df["time"].dt.date
    df["time_only"] = df["time"].dt.time
    df["noisy_day"] = df["date"].isin(noisy_dates)
    df.drop(columns=["time"], inplace=True)
    df.to_csv(f"cleaned_{symbol}_{tf}.csv", index=False)