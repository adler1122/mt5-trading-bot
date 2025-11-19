import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime

def fetch_and_save(symbol, start_date, bars=10000):
    timeframes = {
        "M15": mt5.TIMEFRAME_M15,
        "M30": mt5.TIMEFRAME_M30,
        "H1": mt5.TIMEFRAME_H1,
        "H4": mt5.TIMEFRAME_H4,
        "D1": mt5.TIMEFRAME_D1
    }

    if not mt5.initialize():
        raise RuntimeError("MT5 initialization failed")

    for label, tf in timeframes.items():
        data = mt5.copy_rates_from(symbol, tf, start_date, bars)
        if data is None or len(data) == 0:
            print(f"No data for {symbol} {label}")
            continue
        df = pd.DataFrame(data)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df = df[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
        df.rename(columns={'tick_volume': 'volume'}, inplace=True)
        df.to_csv(f"{symbol}_{label}.csv", index=False)
        print(f"Saved {symbol}_{label}.csv")

    mt5.shutdown()

# Example usage
symbol_input = input("Enter symbol (e.g., XAUUSD): ").strip().upper()
fetch_and_save(symbol_input, datetime(2025, 10,19))