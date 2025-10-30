import pandas as pd
from pandas.errors import EmptyDataError

# Inputs
pattern = input("Enter pattern name (e.g., engulfing, star): ").lower()
symbol = input("Enter symbol (e.g., XAUUSD): ").upper()
timeframes = ["M15", "M30", "H1", "H4"]
directions = ["bullish", "bearish"]

fixed_tp_patterns = ["fvg", "piercing", "marubozu"]
market_movement_patterns = ["orderblock", "engulfing", "star", "threeinside", "tweezer"]

min_size = 200 if pattern in market_movement_patterns else 400

for direction in directions:
    for tf in timeframes:
        filename = f"datasets/{direction}_{pattern}_{symbol}_{tf}.csv"

        try:
            df = pd.read_csv(filename)
            if df.empty:
                print(f"Skipping {filename} — file is empty")
                continue
            if len(df) < min_size:
                print(f"Skipping {filename} — only {len(df)} rows")
                continue

            # Rename columns (adjust per pattern)
            df.rename(columns={
                "day_of_week": "weekday",
                "entry_day_of_week": "entry_weekday",
                "highest_of_day": "is_highest_day",
                "highest_of_week": "is_highest_week",
                "lowest_of_day": "is_lowest_day",
                "lowest_of_week": "is_lowest_week",
                "total_volume": "volume",
                "success": "target",
                "maximum_movement": "target"
            }, inplace=True)

            # Save cleaned dataset with new name
            new_name = f"ml_{direction}_{pattern}_{symbol}_{tf}.csv"
            df.to_csv(new_name, index=False)
            print(f"Saved: {new_name} ({len(df)} rows)")

        except FileNotFoundError:
            print(f"File not found: {filename}")
        except EmptyDataError:
            print(f"Skipping {filename} — empty CSV file")