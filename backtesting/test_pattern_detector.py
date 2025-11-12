class PatternDetector:
    def __init__(self):
        pass

    def detect(self, candles):
        if len(candles) < 3:
            return "no_trade"

        c1 = self._to_dict(candles[-3])
        c2 = self._to_dict(candles[-2])
        c3 = self._to_dict(candles[-1])

        # Bearish FVG
        if (
            c1["low"] > c3["high"] and
            c1["high"] > max(c2["high"], c3["high"]) and
            c3["low"] < min(c1["low"], c2["low"])
        ):
            return "bearish fvg"

        # Bullish Orderblock
        if (
            c2["close"] < c2["open"] and (
                c3["close"] < c3["open"] or
                (c3["close"] > c3["open"] and c3["open"] < c2["close"])
            )
        ):
            return "bullish orderblock"

        # Bearish Orderblock
        if (
            c2["close"] > c2["open"] and (
                c3["close"] > c3["open"] or
                (c3["close"] < c3["open"] and c3["open"] > c2["close"])
            )
        ):
            return "bearish orderblock"

        # Bullish Engulfing
        #body1 = abs(c2["close"] - c2["open"])
        #if (
        #    c2["close"] > c2["open"] and
        #    c3["close"] < c3["open"] and
        #    c3["open"] > c2["close"] - 0.1 * body1 and
        #    c3["close"] < c2["open"] + 0.1 * body1
        #):
        #    return "bullish engulfing"

        return "no_trade"

    def _to_dict(self, candle):
        return {
            "open": candle[1],
            "high": candle[2],
            "low": candle[3],
            "close": candle[4],
            
        }