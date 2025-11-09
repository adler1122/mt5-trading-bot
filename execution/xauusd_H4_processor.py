import joblib
import os
import numpy as np
import pandas as pd
from pattern_detector import PatternDetector
from setup_maker import SetupMaker

class XAUUSD_H4_Processor:
    def __init__(self):
        self.detector = PatternDetector()
        self.setup = SetupMaker()
        self.model_path = "models/xauusd_fvg_bearish_H4_XGBoost.pkl"
        self.scaler_path = "scalers/scaler_xauusd_fvg_bearish_H4.pkl"
        self.model = None
        self.scaler = None
        self._load_model_and_scaler()

    def _load_model_and_scaler(self):
        if os.path.exists(self.model_path):
            self.model = joblib.load(self.model_path)
        if os.path.exists(self.scaler_path):
            self.scaler = joblib.load(self.scaler_path)

    def process_live_candles(self, candles):
        result = self.detector.detect(candles)
        if result == "bearish fvg":
            entry_price = float(candles[-1][2])  # c3 high
            return {
                "fvg": True,
                "entry_price": entry_price,
                "candles": candles[-3:]
            }
        return "no pattern detected"

    def process_trigger(self, candles, entry_date, entry_session):
        
        c1, c2, c3 = candles[-3], candles[-2], candles[-1]

        # Index mapping
        TIMESTAMP = 0
        HIGH = 2
        LOW = 3
        CLOSE = 4

        highs = [float(c1[HIGH]), float(c2[HIGH]), float(c3[HIGH])]
        lows = [float(c1[LOW]), float(c2[LOW]), float(c3[LOW])]

        candle_size = max(highs) - min(lows)
        gap_size = float(c1[LOW]) - float(c3[HIGH])
        percentage = gap_size / float(c3[CLOSE]) if float(c3[CLOSE]) != 0 else 0

        weekday = pd.to_datetime(int(c3[TIMESTAMP]), unit='s').weekday()
        entry_weekday = int(entry_date)
        entry_session_code = int(entry_session)

        # Manual scaling of input features
        candle_min, gap_min, pct_min = self.scaler.data_min_[:3]
        candle_max, gap_max, pct_max = self.scaler.data_max_[:3]

        scaled_candle = (candle_size - candle_min) / (candle_max - candle_min)
        scaled_gap = (gap_size - gap_min) / (gap_max - gap_min)
        scaled_pct = (percentage - pct_min) / (pct_max - pct_min)

        vector = [scaled_candle, scaled_gap, scaled_pct, int(weekday), entry_weekday, entry_session_code]

        prediction = self.model.predict([vector])[0]  # target is not scaled

        signal = self.setup.make_signal(
            pattern="fvg",
            direction="bearish",
            prediction=prediction,
            current_price=float(c3[CLOSE]),
            candle=c3,
            timeframe="H4"
        )
        return signal