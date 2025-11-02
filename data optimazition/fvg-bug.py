import pandas as pd

# Load the CSV
symbol=input("enter symbol: ")
directions=["bullish","bearish"]
for direction in directions:
    name=f"ml_{direction}_fvg_{symbol}_M15.csv"
    df = pd.read_csv(f"ml datasets/{symbol}/fvg/{name}")
    df.dropna(inplace=True) 
    #print(df[df.columns[-1]].unique())
    #print(df[df.columns[-1]].dtype)

    last_col = df.columns[-1]
    df[last_col] = df[last_col].astype(bool)
    print(df[df.columns[-1]].dtype)
    df[last_col] = df[last_col].astype(int)
    print(df[df.columns[-1]].dtype)

    
    #df[df.columns[-1]] = df[df.columns[-1]].map({"True": 1, "False": 0})
    #df[df.columns[-1]] = df[df.columns[-1]].astype(bool).astype(int)
    
    df.to_csv(name, index=False)