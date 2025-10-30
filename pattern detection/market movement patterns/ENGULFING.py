import pandas as pd

symbol = input("Enter symbol: ")
timeframes = ["M15", "M30", "H1", "H4"]
BROKER_OFFSET = -2

def get_session(broker_hour):
    utc_hour = (broker_hour + BROKER_OFFSET) % 24
    if 0 <= utc_hour < 6: return "Sydney"
    elif 6 <= utc_hour < 12: return "Tokyo"
    elif 12 <= utc_hour < 18: return "London"
    else: return "New York"

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
        body1 = abs(c1["open"] - c1["close"])

        # Softened Bullish Engulfing
        if (
            c1["close"] < c1["open"] and
            c2["close"] > c2["open"] and
            c2["open"] < c1["close"] + 0.1 * body1 and
            c2["close"] > c1["open"] - 0.1 * body1
        ):
            break_price = c2["close"]
            max_move = 0
            returned = False
            for j in range(i + 2, len(df)):
                candle = df.iloc[j]
                if candle["low"] <= break_price:
                    returned = True
                    break
                move = candle["high"] - break_price
                if move > max_move: max_move = move
            if max_move > 0:
                same_day = df[(df["date"] == c2["date"]) & (df["time"] <= c2["time"])]
                same_week = df[(pd.to_datetime(df["date"]).dt.isocalendar().week == pd.to_datetime(c2["date"]).isocalendar().week) & (df["time"] <= c2["time"])]
                lowest_day = min(c1["low"], c2["low"]) <= same_day["low"].min()
                lowest_week = min(c1["low"], c2["low"]) <= same_week["low"].min()
                bullish_records.append({
                    "noisy_day": c2["noisy_day"],
                    "highest_of_day": lowest_day,
                    "highest_of_week": lowest_week,
                    "total_volume": c1["tick_volume"] + c2["tick_volume"],
                    "session": c2["session"],
                    "day_of_week": c2["day_of_week"],
                    "maximum_movement": round(max_move, 2)
                })

        # Softened Bearish Engulfing
        elif (
            c1["close"] > c1["open"] and
            c2["close"] < c2["open"] and
            c2["open"] > c1["close"] - 0.1 * body1 and
            c2["close"] < c1["open"] + 0.1 * body1
        ):
            break_price = c2["close"]
            max_move = 0
            returned = False
            for j in range(i + 2, len(df)):
                candle = df.iloc[j]
                if candle["high"] >= break_price:
                    returned = True
                    break
                move = break_price - candle["low"]
                if move > max_move: max_move = move
            if max_move > 0:
                same_day = df[(df["date"] == c2["date"]) & (df["time"] <= c2["time"])]
                same_week = df[(pd.to_datetime(df["date"]).dt.isocalendar().week == pd.to_datetime(c2["date"]).isocalendar().week) & (df["time"] <= c2["time"])]
                highest_day = max(c1["high"], c2["high"]) >= same_day["high"].max()
                highest_week = max(c1["high"], c2["high"]) >= same_week["high"].max()
                bearish_records.append({
                    "noisy_day": c2["noisy_day"],
                    "highest_of_day": highest_day,
                    "highest_of_week": highest_week,
                    "total_volume": c1["tick_volume"] + c2["tick_volume"],
                    "session": c2["session"],
                    "day_of_week": c2["day_of_week"],
                    "maximum_movement": round(max_move, 2)
                })

    pd.DataFrame(bullish_records).to_csv(f"bullish_engulfing_{symbol}_{tf}.csv", index=False)
    pd.DataFrame(bearish_records).to_csv(f"bearish_engulfing_{symbol}_{tf}.csv", index=False)