import joblib
import os
import numpy as np
import pandas as pd
from pattern_detector import PatternDetector
from setup_maker import SetupMaker

class XAUUSD_M30_Processor:
    def __init__(self):
        self.detector = PatternDetector()
        self.setup = SetupMaker()

        self.model_paths = {
            "bullish": "models/xauusd_orderblock_bullish_M30_SVR.pkl",
            "bearish": "models/xauusd_orderblock_bearish_M30_GradientBoosting.pkl"
        }
        self.scaler_paths = {
            "bullish": "scalers/scaler_xauusd_orderblock_bullish_M30.pkl",
            "bearish": "scalers/scaler_xauusd_orderblock_bearish_M30.pkl"
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
        return "no pattern detected"

    def process_orderblock_trigger(self, candles, noisy_day, is_highest_day, is_highest_week, session_code, direction):


        c1, c2 = candles[-2], candles[-1]

        # Index mapping
        TIMESTAMP = 0
        VOLUME = 5
        CLOSE = 4

        weekday = pd.to_datetime(int(c2[TIMESTAMP]), unit='s').weekday()
        volume = float(c1[VOLUME]) + float(c2[VOLUME])

        # Extract direction-specific min/max
        scaler = self.scalers[direction]
        volume_min = scaler.data_min_[0]
        volume_max = scaler.data_max_[0]
        target_min = scaler.data_min_[1]
        target_max = scaler.data_max_[1]

        # Manually scale volume
        scaled_volume = (volume - volume_min) / (volume_max - volume_min)

        # Build vector
        if direction == "bullish":
            vector = [ int(noisy_day), int(is_highest_day), int(is_highest_week), scaled_volume, int(session_code)]
        else:
            vector = [int(noisy_day), int(is_highest_day), int(is_highest_week), scaled_volume, int(session_code), int(weekday)]

        # Predict and unscale
        scaled_prediction = self.models[direction].predict([vector])[0]
        unscaled_prediction = scaled_prediction * (target_max - target_min) + target_min

        signal = self.setup.make_signal(
            pattern="orderblock",
            direction=direction,
            prediction=unscaled_prediction,
            current_price=float(c2[CLOSE]),
            candle=c2,
            timeframe="M30"
        )
        return signal