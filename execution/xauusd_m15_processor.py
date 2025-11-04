import joblib
import os
import numpy as np
import pandas as pd
from pattern_detector import PatternDetector
from setup_maker import SetupMaker

class XAUUSD_M15_Processor:
    def __init__(self):
        self.detector = PatternDetector()
        self.setup = SetupMaker()

        self.model_paths = {
            "bearish fvg": "models/xauusd_fvg_bearish_M15_KNN.pkl",
            "bullish engulfing": "models/xauusd_engulfing_bullish_M15_SVR.pkl",
            "bullish orderblock": "models/xauusd_orderblock_bullish_M15_SVR.pkl",
            "bearish orderblock": "models/xauusd_orderblock_bearish_M15_SVR.pkl"
        }

        self.scaler_paths = {
            "bearish fvg": "scalers/scaler_xauusd_fvg_bearish_M15.pkl",
            "bullish engulfing": "scalers/scaler_xauusd_engulfing_bullish_M15.pkl",
            "bullish orderblock": "scalers/scaler_xauusd_orderblock_bullish_M15.pkl",
            "bearish orderblock": "scalers/scaler_xauusd_orderblock_bearish_M15.pkl"
        }

        self.models = {}
        self.scalers = {}
        self._load_models_and_scalers()

    def _load_models_and_scalers(self):
        for pattern in self.model_paths:
            if os.path.exists(self.model_paths[pattern]):
                self.models[pattern] = joblib.load(self.model_paths[pattern])
            if os.path.exists(self.scaler_paths[pattern]):
                self.scalers[pattern] = joblib.load(self.scaler_paths[pattern])

    def process_live_candles(self, candles):
        result = self.detector.detect(candles)
        if result in self.models:
            return {
                "pattern": result,
                "candles": candles[-3:] if result == "bearish fvg" else candles[-2:]
            }
        return "no_trade"

    def process_trigger(self, candles, pattern, noisy_day=None, is_highest_day=None, is_highest_week=None, session_code=None):
        if pattern not in self.models or pattern not in self.scalers:
            return "no_trade"

        if pattern == "bearish fvg":
            return self._process_fvg(candles, pattern)

        return self._process_orderblock_or_engulfing(candles, pattern, noisy_day, is_highest_day, is_highest_week, session_code)

    def _process_fvg(self, candles, pattern):
        c1, c2, c3 = candles[-3], candles[-2], candles[-1]

        # Index mapping
        HIGH, LOW, CLOSE, TIMESTAMP = 2, 3, 4, 0

        highs = [float(c1[HIGH]), float(c2[HIGH]), float(c3[HIGH])]
        lows = [float(c1[LOW]), float(c2[LOW]), float(c3[LOW])]

        candle_size = max(highs) - min(lows
        )
        gap_size = float(c1[LOW]) - float(c3[HIGH])
        percentage = gap_size / float(c3[CLOSE]) if float(c3[CLOSE]) != 0 else 0
        weekday = pd.to_datetime(int(c3[TIMESTAMP]), unit='s').weekday()

        vector = [float(candle_size), float(gap_size), float(percentage), int(weekday)]

        scaler = self.scalers[pattern]
        scaled = scaler.transform(np.array([vector]))
        scaled_prediction = self.models[pattern].predict(scaled)[0]
        unscaled_prediction = scaler.inverse_transform([[scaled_prediction] + [0] * (len(vector) - 1)])[0][0]

        signal = self.setup.make_signal(
            pattern="fvg",
            direction="bearish",
            prediction=unscaled_prediction,
            current_price=float(c3[CLOSE]),
            candle=c3,
            timeframe="M15"
        )
        return signal

    def _process_orderblock_or_engulfing(self, candles, pattern, noisy_day, is_highest_day, is_highest_week, session_code):
        c1, c2 = candles[-2], candles[-1]

        # Index mapping
        TIMESTAMP = 0
        VOLUME = 5
        CLOSE = 4

        volume = float(c1[VOLUME]) + float(c2[VOLUME])
        weekday = pd.to_datetime(int(c2[TIMESTAMP]), unit='s').weekday()

        if pattern == "bullish engulfing":
            vector = [
                int(noisy_day),
                int(is_highest_day),
                int(is_highest_week),
                float(volume),
                int(session_code),
                int(weekday)
            ]
        elif pattern == "bullish orderblock":
            vector = [
                int(noisy_day),
                int(is_highest_day),
                int(is_highest_week),
                float(volume),
                int(session_code)
            ]
        elif pattern == "bearish orderblock":
            vector = [
                int(noisy_day),
                int(is_highest_week),
                float(volume),
                int(session_code),
                int(weekday)
            ]
        else:
            return "no_trade"

        scaler = self.scalers[pattern]
        scaled = scaler.transform(np.array([vector]))
        scaled_prediction = self.models[pattern].predict(scaled)[0]
        unscaled_prediction = scaler.inverse_transform([[scaled_prediction] + [0] * (len(vector) - 1)])[0][0]

        signal = self.setup.make_signal(
            pattern="orderblock" if "orderblock" in pattern else "engulfing",
            direction=pattern.split()[0],
            prediction=unscaled_prediction,
            current_price=float(c2[CLOSE]),
            candle=c2,
            timeframe="M15"
        )
        return signal