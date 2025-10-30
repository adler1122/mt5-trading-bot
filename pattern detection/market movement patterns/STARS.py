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

    for i in range(len(df) - 3):
        c1, c2, c3 = df.iloc[i], df.iloc[i+1], df.iloc[i+2]
        future = df.iloc[i+3:]

        # Morning Star (bullish reversal)
        if (
            c1["close"] < c1["open"] and
            c2["low"] < c1["close"] and c2["high"] < c1["open"] and
            c3["close"] > c3["open"] and
            c3["close"] > (c1["open"] + c1["close"]) / 2
        ):
            break_price = c3["close"]
            max_move = 0
            returned = False
            for j in range(i + 3, len(df)):
                candle = df.iloc[j]
                if candle["low"] <= break_price:
                    returned = True
                    break
                move = candle["high"] - break_price
                if move > max_move: max_move = move
            if max_move > 0:
                same_day = df[(df["date"] == c3["date"]) & (df["time"] <= c3["time"])]
                same_week = df[(pd.to_datetime(df["date"]).dt.isocalendar().week == pd.to_datetime(c3["date"]).isocalendar().week) & (df["time"] <= c3["time"])]
                lowest_day = min(c1["low"], c2["low"], c3["low"]) <= same_day["low"].min()
                lowest_week = min(c1["low"], c2["low"], c3["low"]) <= same_week["low"].min()
                bullish_records.append({
                    "noisy_day": c3["noisy_day"],
                    "highest_of_day": lowest_day,
                    "highest_of_week": lowest_week,
                    "total_volume": c1["tick_volume"] + c2["tick_volume"] + c3["tick_volume"],
                    "session": c3["session"],
                    "day_of_week": c3["day_of_week"],
                    "maximum_movement": round(max_move, 2)
                })

        # Evening Star (bearish reversal)
        elif (
            c1["close"] > c1["open"] and
            c2["high"] > c1["close"] and c2["low"] > c1["open"] and
            c3["close"] < c3["open"] and
            c3["close"] < (c1["open"] + c1["close"]) / 2
        ):
            break_price = c3["close"]
            max_move = 0
            returned = False
            for j in range(i + 3, len(df)):
                candle = df.iloc[j]
                if candle["high"] >= break_price:
                    returned = True
                    break
                move = break_price - candle["low"]
                if move > max_move: max_move = move
            if max_move > 0:
                same_day = df[(df["date"] == c3["date"]) & (df["time"] <= c3["time"])]
                same_week = df[(pd.to_datetime(df["date"]).dt.isocalendar().week == pd.to_datetime(c3["date"]).isocalendar().week) & (df["time"] <= c3["time"])]
                highest_day = max(c1["high"], c2["high"], c3["high"]) >= same_day["high"].max()
                highest_week = max(c1["high"], c2["high"], c3["high"]) >= same_week["high"].max()
                bearish_records.append({
                    "noisy_day": c3["noisy_day"],
                    "highest_of_day": highest_day,
                    "highest_of_week": highest_week,
                    "total_volume": c1["tick_volume"] + c2["tick_volume"] + c3["tick_volume"],
                    "session": c3["session"],
                    "day_of_week": c3["day_of_week"],
                    "maximum_movement": round(max_move, 2)
                })

    pd.DataFrame(bullish_records).to_csv(f"bullish_star_{symbol}_{tf}.csv", index=False)
    pd.DataFrame(bearish_records).to_csv(f"bearish_star_{symbol}_{tf}.csv", index=False)