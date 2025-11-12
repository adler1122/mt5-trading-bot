class SetupMaker:
    def __init__(self):
        pass

    def make_signal(self, pattern, direction, prediction, current_price, candle, timeframe):
        entry = float(current_price)

        if pattern == "bearish fvg":
            gap = abs(float(candle[3]) - float(candle[2]))  # low - high

            # Classification-based order type logic
            if direction == "bearish":
                order_type = "buy" if prediction == 0 else "sell"
            elif direction == "bullish":
                order_type = "sell" if prediction == 0 else "buy"
            else:
                return "no_trade"

            if prediction == 0:
                tp = entry + gap
                sl = entry - gap
            else:
                tp = entry - gap
                sl = entry + gap

            return {
                "pattern": pattern,
                "direction": direction,
                "order_type": order_type,
                "entry": entry,
                "tp": round(tp, 2),
                "sl": round(sl, 2),
                "timeframe": timeframe,
                "candles": candle
            }

        # Regression-based setups
        c1, c2 = candle[1], candle[2]  # candle is [c0,c1, c2]
        order_type = "buy" if direction == "bullish" else "sell"

        if pattern == "bullish orderblock" or pattern == "bullish engulfing":
            sl = min(float(c1[3]), float(c2[3])) - 0.4
            tp = entry + prediction

        elif pattern == "bearish orderblock":
            sl = max(float(c1[2]), float(c2[2])) + 0.4
            tp = entry - prediction

        else:
            return "no registered pattern"

        # R:R check
        if abs(tp - entry) <= abs(sl - entry):
            return "no trade bad r:r"

        return {
            "pattern": pattern,
            "direction": direction,
            "order_type": order_type,
            "entry": entry,
            "tp": round(tp, 2),
            "sl": round(sl, 2),
            "timeframe": timeframe,
            "candle": candle
        }