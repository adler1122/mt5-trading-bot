import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

# --- Initialize MT5 ---
if not mt5.initialize():
    raise RuntimeError("MT5 initialization failed")

# --- Symbol and Timeframes ---
symbol = input("Enter symbol: ").upper()  # Ensure uppercase for broker compatibility
timeframes = {
    "M15": mt5.TIMEFRAME_M15,
    "M30": mt5.TIMEFRAME_M30,
    "H1": mt5.TIMEFRAME_H1,
    "H4": mt5.TIMEFRAME_H4,
    "D1": mt5.TIMEFRAME_D1
}

# --- Fixed Start Date for non-M15 ---
fixed_start_date = datetime(2021, 8, 9) # get this from first row of m15 tf 
end_date = datetime.now()

# --- Download and Save ---
for label, tf in timeframes.items():
    print(f"Downloading {label} data...")

    if label == "M15":
        rates = mt5.copy_rates_from_pos(symbol, tf, 0, 99998)
        if rates is None or len(rates) == 0:
            print("No M15 data available")
            continue
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        first_time = df['time'].iloc[0]
        print(f"First M15 candle date: {first_time}")
    else:
        rates = mt5.copy_rates_range(symbol, tf, fixed_start_date, end_date)
        if rates is None or len(rates) == 0:
            print(f"No data for {label}")
            continue
        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')

    df.to_csv(f"{symbol}_{label}.csv", index=False)
    print(f"Saved {symbol}_{label}.csv")

# --- Shutdown MT5 ---
mt5.shutdown()