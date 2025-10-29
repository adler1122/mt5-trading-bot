This module performs structured data cleaning on gold candlestick data extracted from MetaTrader 5 (MT5). The data is sourced from the default MT5 demo server (typically MetaQuotes) and includes five timeframes: 15-minute, 30-minute, 1-hour, 4-hour, and 1-day. Only data from January 1, 2023 onward is used.

Cleaning Steps
    Column Filtering
        For all timeframes, the following columns are removed:
 	    represents the bid-ask difference, not relevant for this analysis
 	    always zero in MT5 demo data
    Daily Candle Analysis (1440-minute timeframe)
 	    A new feature  is created as 
 	    IQR filtering is applied to both  and 
 	    Any row with values outside the IQR bounds is flagged as a noisy day
	    The corresponding dates are saved in a set for downstream filtering
    oisy Day Flagging in Intra-Day Timeframes
        For the 15-minute, 30-minute, 1-hour, and 4-hour datasets:
 	    Rows before 2023 are removed
 	    The  column is split into separate  and  columns
 	    A new column  is added and set to  if the row’s date matches a flagged noisy day, otherwise 

The daily timeframe is used only for noise detection and is excluded from modeling. No further cleaning is required, as MT5 data is free of missing values and duplicate rows.