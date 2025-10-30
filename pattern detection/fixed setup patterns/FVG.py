import pandas as pd

symbol = input("Enter symbol: ")
timeframes = ["M15", "M30", "H1", "H4"]

BROKER_OFFSET = -2

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

    for i in range(len(df) - 3):
        c1, c2, c3 = df.iloc[i], df.iloc[i+1], df.iloc[i+2]

        # Bullish FVG
        if (
            c1["high"] < c3["low"] and
            c3["high"] > max(c1["high"], c2["high"]) and
            c1["low"] < min(c2["low"], c3["low"])
        ):
            entry = c3["low"]
            sl = c1["high"]
            tp = entry + (sl - entry)
            gap_size = c3["low"] - c1["high"]
            entry_triggered = False
            trade_result = None
            entry_time = None

            for j in range(i + 3, len(df)):
                candle = df.iloc[j]
                if not entry_triggered and candle["low"] <= entry:
                    entry_triggered = True
                    entry_time = candle["time"]
                elif entry_triggered:
                    if candle["high"] >= tp:
                        trade_result = True
                        break
                    elif candle["low"] <= sl:
                        trade_result = False
                        break

            if entry_triggered:
                candle_size = round(max(c1["high"], c2["high"], c3["high"]) - min(c1["low"], c2["low"], c3["low"]), 2)
                percentage = candle_size / c3["high"] if c3["high"] != 0 else 0
                noisy = c3["noisy_day"]
                volume_sum = c1["tick_volume"] + c2["tick_volume"] + c3["tick_volume"]
                entry_day = entry_time.weekday()
                entry_session = get_session(entry_time.hour)
                same_day = df[(df["date"] == c3["date"]) & (df["time"] <= c3["time"])]
                same_week = df[(pd.to_datetime(df["date"]).dt.isocalendar().week == pd.to_datetime(c3["date"]).isocalendar().week) & (df["time"] <= c3["time"])]
                highest_day = c3["high"] >= same_day["high"].max()
                highest_week = c3["high"] >= same_week["high"].max()

                bullish_records.append({
                    "candle_size": candle_size,
                    "gap_size": gap_size,
                    "noisy_day": noisy,
                    "percentage": percentage,
                    "day_of_week": c3["day_of_week"],
                    "session": c3["session"],
                    "entry_day_of_week": entry_day,
                    "entry_session": entry_session,
                    "highest_of_day": highest_day,
                    "highest_of_week": highest_week,
                    "total_volume": volume_sum,
                    "success": trade_result
                })

        # Bearish FVG
        elif (
            c1["low"] > c3["high"] and
            c1["high"] > max(c2["high"], c3["high"]) and
            c3["low"] < min(c1["low"], c2["low"])
        ):
            entry = c3["high"]
            tp = entry - (c1["low"] - c3["high"])
            sl = entry + (c1["low"] - c3["high"])
            gap_size = c1["low"] - c3["high"]
            entry_triggered = False
            trade_result = None
            entry_time = None

            for j in range(i + 3, len(df)):
                candle = df.iloc[j]
                if not entry_triggered and candle["high"] >= entry:
                    entry_triggered = True
                    entry_time = candle["time"]
                elif entry_triggered:
                    if candle["low"] <= tp:
                        trade_result = True
                        break
                    elif candle["high"] >= sl:
                        trade_result = False
                        break

            if entry_triggered:
                candle_size = round(max(c1["high"], c2["high"], c3["high"]) - min(c1["low"], c2["low"], c3["low"]), 2)
                percentage = candle_size / c3["high"] if c3["high"] != 0 else 0
                noisy = c3["noisy_day"]
                volume_sum = c1["tick_volume"] + c2["tick_volume"] + c3["tick_volume"]
                entry_day = entry_time.weekday()
                entry_session = get_session(entry_time.hour)
                same_day = df[(df["date"] == c3["date"]) & (df["time"] <= c3["time"])]
                same_week = df[(pd.to_datetime(df["date"]).dt.isocalendar().week == pd.to_datetime(c3["date"]).isocalendar().week) & (df["time"] <= c3["time"])]
                lowest_day = c3["low"] <= same_day["low"].min()
                lowest_week = c3["low"] <= same_week["low"].min()

                bearish_records.append({
                    "candle_size": candle_size,
                    "gap_size": gap_size,
                    "noisy_day": noisy,
                    "percentage": percentage,
                    "day_of_week": c3["day_of_week"],
                    "session": c3["session"],
                    "entry_day_of_week": entry_day,
                    "entry_session": entry_session,
                    "lowest_of_day": lowest_day,
                    "lowest_of_week": lowest_week,
                    "total_volume": volume_sum,
                    "success": trade_result
                })

    pd.DataFrame(bullish_records).to_csv(f"bullish_fvg_{symbol}_{tf}.csv", index=False)
    pd.DataFrame(bearish_records).to_csv(f"bearish_fvg_{symbol}_{tf}.csv", index=False)