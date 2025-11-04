import joblib
import os
import numpy as np
import pandas as pd
from pattern_detector import PatternDetector
from setup_maker import SetupMaker

class XAUUSD_H1_Processor:
    def __init__(self):
        self.detector = PatternDetector()
        self.setup = SetupMaker()

        self.model_paths = {
            "bullish": "models/xauusd_orderblock_bullish_H1_SVR.pkl",
            "bearish": "models/xauusd_orderblock_bearish_H1_SVR.pkl"
        }
        self.scaler_paths = {
            "bullish": "scalers/scaler_xauusd_orderblock_bullish_H1.pkl",
            "bearish": "scalers/scaler_xauusd_orderblock_bearish_H1.pkl"
        }

        self.models = {}
        self.scalers = {}
        self._load_models_and_scalers()

    def _load_models_and_scalers(self):
        for direction in ["bullish", "bearish"]:
            model_path = self.model_paths[direction]
            scaler_path = self.scaler_paths[direction]

            if os.path.exists(model_path):
                self.models[direction] = joblib.load(model_path)
            if os.path.exists(scaler_path):
                self.scalers[direction] = joblib.load(scaler_path)

    def process_live_candles(self, candles):
        result = self.detector.detect(candles)
        if result in ["bullish orderblock", "bearish orderblock"]:
            direction = result.split()[0]
            return {
                "pattern": "orderblock",
                "direction": direction,
                "candles": candles[-2:]
            }
        return "no_trade"

    def process_orderblock_trigger(self, candles, noisy_day, is_highest_day, is_highest_week, session_code, direction):
        if len(candles) < 2:
            return "no_trade"

        if direction not in self.models or direction not in self.scalers:
            return "no_trade"

        c1, c2 = candles[-2], candles[-1]

        # Index mapping
        TIMESTAMP = 0
        VOLUME = 5
        CLOSE = 4

        volume = float(c1[VOLUME]) + float(c2[VOLUME])
        scaler = self.scalers[direction]

        if direction == "bullish":
            weekday = pd.to_datetime(int(c2[TIMESTAMP]), unit='s').weekday()
            vector = [
                int(noisy_day),
                int(is_highest_day),
                int(is_highest_week),
                float(volume),
                int(session_code),
                int(weekday)
            ]
        else:  # bearish
            vector = [
                int(noisy_day),
                int(is_highest_day),
                int(is_highest_week),
                float(volume),
                int(session_code)
            ]

        scaled = scaler.transform(np.array([vector]))
        scaled_prediction = self.models[direction].predict(scaled)[0]
        unscaled_prediction = scaler.inverse_transform([[scaled_prediction] + [0] * (len(vector) - 1)])[0][0]

        signal = self.setup.make_signal(
            pattern="orderblock",
            direction=direction,
            prediction=unscaled_prediction,
            current_price=float(c2[CLOSE]),
            candle=c2,
            timeframe="H1"
        )
        return signal