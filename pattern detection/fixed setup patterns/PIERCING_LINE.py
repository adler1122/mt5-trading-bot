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

    for i in range(len(df) - 2):
        c1, c2 = df.iloc[i], df.iloc[i+1]
        future = df.iloc[i+2:]

        # Bullish Piercing Line
        if (
            c1["close"] < c1["open"] and  # first candle bearish
            c2["open"] < c1["low"] and
            c2["close"] > (c1["open"] + c1["close"]) / 2
        ):
            entry = c2["close"]
            sl = c2["low"]
            tp = entry + abs(c1["open"] - c1["close"])
            entry_triggered = False
            trade_result = None

            for j in range(i + 2, len(df)):
                candle = df.iloc[j]
                if not entry_triggered and candle["low"] <= entry:
                    entry_triggered = True
                elif entry_triggered:
                    if candle["high"] >= tp:
                        trade_result = True
                        break
                    elif candle["low"] <= sl:
                        trade_result = False
                        break

            if entry_triggered:
                candle_size = round(abs(c1["open"] - c1["close"]), 2)
                noisy = c2["noisy_day"]
                volume_sum = c1["tick_volume"] + c2["tick_volume"]
                same_day = df[(df["date"] == c2["date"]) & (df["time"] <= c2["time"])]
                same_week = df[(pd.to_datetime(df["date"]).dt.isocalendar().week == pd.to_datetime(c2["date"]).isocalendar().week) & (df["time"] <= c2["time"])]
                lowest_day = c2["low"] <= same_day["low"].min()
                lowest_week = c2["low"] <= same_week["low"].min()

                bullish_records.append({
                    "candle_size": candle_size,
                    "noisy_day": noisy,
                    "day_of_week": c2["day_of_week"],
                    "session": c2["session"],
                    "lowest_of_day": lowest_day,
                    "lowest_of_week": lowest_week,
                    "total_volume": volume_sum,
                    "success": trade_result
                })

        # Bearish Piercing Line (Dark Cloud Cover)
        elif (
            c1["close"] > c1["open"] and  # first candle bullish
            c2["open"] > c1["high"] and
            c2["close"] < (c1["open"] + c1["close"]) / 2
        ):
            entry = c2["close"]
            tp = entry - abs(c1["close"] - c1["open"])
            sl = c2["high"]
            entry_triggered = False
            trade_result = None

            for j in range(i + 2, len(df)):
                candle = df.iloc[j]
                if not entry_triggered and candle["high"] >= entry:
                    entry_triggered = True
                elif entry_triggered:
                    if candle["low"] <= tp:
                        trade_result = True
                        break
                    elif candle["high"] >= sl:
                        trade_result = False
                        break

            if entry_triggered:
                candle_size = round(abs(c1["close"] - c1["open"]), 2)
                noisy = c2["noisy_day"]
                volume_sum = c1["tick_volume"] + c2["tick_volume"]
                same_day = df[(df["date"] == c2["date"]) & (df["time"] <= c2["time"])]
                same_week = df[(pd.to_datetime(df["date"]).dt.isocalendar().week == pd.to_datetime(c2["date"]).isocalendar().week) & (df["time"] <= c2["time"])]
                highest_day = c2["high"] >= same_day["high"].max()
                highest_week = c2["high"] >= same_week["high"].max()

                bearish_records.append({
                    "candle_size": candle_size,
                    "noisy_day": noisy,
                    "day_of_week": c2["day_of_week"],
                    "session": c2["session"],
                    "highest_of_day": highest_day,
                    "highest_of_week": highest_week,
                    "total_volume": volume_sum,
                    "success": trade_result
                })

    pd.DataFrame(bullish_records).to_csv(f"bullish_piercing_{symbol}_{tf}.csv", index=False)
    pd.DataFrame(bearish_records).to_csv(f"bearish_piercing_{symbol}_{tf}.csv", index=False)