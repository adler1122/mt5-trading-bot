Gold Candle Data Extraction from MT5
This project extracts historical candlestick data for gold (XAUUSD) from MetaTrader 5 (MT5) using Python. The data is retrieved directly from the default MT5 demo server, which is typically MetaQuotes.
We work with five timeframes:
15-minute
30-minute
1-hour
4-hour
1-day
The dataset includes key features such as open, high, low, close, volume, and timestamp. For each timeframe, data is collected from January 1, 2023, up to the current date.
The data is saved in separate CSV files for each timeframe, making it easy to use in downstream tasks such as pattern detection, feature engineering, and model training.
To run the extraction script, make sure MetaTrader 5 is installed and running, and that you're logged into the demo account. The script uses the MetaTrader5 Python package to connect and pull data