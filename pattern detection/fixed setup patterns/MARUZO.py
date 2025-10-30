import pandas as pd

symbol = input("Enter symbol: ")
timeframes = ["M15", "M30", "H1", "H4"]

BROKER_OFFSET = -2  # Broker time minus 2 hours to get UTC

def get_session(broker_hour):
    utc_hour = (broker_hour + BROKER_OFFSET) % 24
    if 0 <= utc_hour < 6:
        return "Sydney"
    elif 6 <= utc_hour < 12:
        return "Tokyo"
    elif 12 <= utc_hour < 18:
        return "London"
    else:
        return "New York"

for tf in timeframes:
    df = pd.read_csv(f"datasets/cleaned_{symbol}_{tf}.csv")
    df["time"] = pd.to_datetime(df["date"].astype(str) + " " + df["time_only"].astype(str))
    df["day_of_week"] = pd.to_datetime(df["date"]).dt.weekday
    df["session"] = df["time"].dt.hour.apply(get_session)

    bullish_records = []
    bearish_records = []

    for i in range(len(df)):
        row = df.iloc[i]
        date = row["date"]
        week = pd.to_datetime(date).isocalendar().week
        high = row["high"]
        low = row["low"]
        close = row["close"]
        open_ = row["open"]
        time = row["time"]
        noisy = row["noisy_day"]
        volume = row["tick_volume"]

        body = abs(close - open_)
        if body == 0:
            continue

        upper_wick = high - max(open_, close)
        lower_wick = min(open_, close) - low

        if (upper_wick < 0.1 * body) and (lower_wick < 0.1 * body):
            candle_size = round(high - low, 2)
            same_day = df[(df["date"] == date) & (df["time"] <= time)]
            same_week = df[(pd.to_datetime(df["date"]).dt.isocalendar().week == week) & (df["time"] <= time)]
            percentage = candle_size / high if high != 0 else 0

            if close > open_:
                entry = close
                tp = close + candle_size
                sl = close - candle_size
                future = df.iloc[i+1:i+10]
                hit_tp = any(future["high"] >= tp)
                hit_sl = any(future["low"] <= sl)
                success = hit_tp and not hit_sl
                highest_day = high >= same_day["high"].max()
                highest_week = high >= same_week["high"].max()

                bullish_records.append({
                    "candle_size": candle_size,
                    "noisy_day": noisy,
                    "percentage": percentage,
                    "day_of_week": row["day_of_week"],
                    "session": row["session"],
                    "highest_of_day": highest_day,
                    "highest_of_week": highest_week,
                    "volume": volume,
                    "success": success
                })

            elif close < open_:
                entry = close
                tp = close - candle_size
                sl = close + candle_size
                future = df.iloc[i+1:i+10]
                hit_tp = any(future["low"] <= tp)
                hit_sl = any(future["high"] >= sl)
                success = hit_tp and not hit_sl
                lowest_day = low <= same_day["low"].min()
                lowest_week = low <= same_week["low"].min()

                bearish_records.append({
                    "candle_size": candle_size,
                    "noisy_day": noisy,
                    "percentage": percentage,
                    "day_of_week": row["day_of_week"],
                    "session": row["session"],
                    "lowest_of_day": lowest_day,
                    "lowest_of_week": lowest_week,
                    "volume": volume,
                    "success": success
                })

    pd.DataFrame(bullish_records).to_csv(f"bullish_marubozu_{symbol}_{tf}.csv", index=False)
    pd.DataFrame(bearish_records).to_csv(f"bearish_marubozu_{symbol}_{tf}.csv", index=False)