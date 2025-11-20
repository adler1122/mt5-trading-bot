MT5 Trading Bot (XAUUSD Focus)

This project is a machine learning powered trading bot for MetaTrader 5, designed around a data mining workflow:

Data Preparation
   
  	Cleaned OHLC data and extracted candlestick patterns.

  	Engineered features: session, volume, day of week, daily/weekly extremes.

  	Built datasets across M15, M30, H1, H4 timeframes.

 Modeling

  	Treated patterns as either classification (TP vs SL) or regression (movement magnitude).

  	Applied correlation checks, manual encoding, and scaling.

  	Tested 6 ML models per pattern.

  	Selection criteria:

  	Classifiers: balanced (TP/total_pos)*(TN/total_neg) > 0.25.

  	Regression: TP ratio > 50%, TP : pred < true

  	Stored best model per pattern/direction.

 Execution
 	
  	Backtesting engine for XAUUSD:

  	Simulates trades candle-by-candle.

  	Handles ambiguous candles (both TP and SL hit) with best-case and worst-case resolution.

  	Real-time engine:

  	Monitors live market data.

  	Executes trades when validated patterns appear.

  	Simple risk-based lot size

Key Features

   	Dual-mode backtesting (best vs worst case).
   	
    Modular ML pipeline for candlestick pattern prediction.
   	
  	Real-time trading integration with MetaTrader 5.

  	Focused on XAUUSD but extensible to other instruments.
