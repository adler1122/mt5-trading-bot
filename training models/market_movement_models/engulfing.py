import pandas as pd
import os
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor

# Inputs
symbol = input("Enter symbol (e.g., xauusd): ").lower()
pattern = "engulfing"  # Changed from "orderblock"
base_path = f"ml datasets/{symbol}/{pattern}"

# Models to test
models = {
    "RandomForest": RandomForestRegressor(),
    "GradientBoosting": GradientBoostingRegressor(),
    "LinearRegression": LinearRegression(),
    "KNN": KNeighborsRegressor(),
    "SVR": SVR(),
    "XGBoost": XGBRegressor()
}

results = []
balance_curves = defaultdict(lambda: defaultdict(list))  # {(direction, timeframe): {model: [balance]}}

for filename in os.listdir(base_path):
    if not filename.endswith(".csv"):
        continue

    path = os.path.join(base_path, filename)
    df = pd.read_csv(path)

    if "target" not in df.columns:
        continue

    # Extract direction and timeframe
    parts = filename.replace(".csv", "").split("_")
    if len(parts) < 4:
        print(f"Skipping malformed filename: {filename}")
        continue
    direction = parts[1]
    timeframe = parts[-1]

    # Split data
    split_idx = int(len(df) * 0.9)
    X = df.drop(columns=["target"])
    y = df["target"]

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        # Evaluation
        balance = 1000
        curve = []
        for pred, true in zip(preds, y_test):
            if pred > true:
                balance -= 10 * true
            elif true > pred:
                balance += 10 * pred
            curve.append(balance)

        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)

        results.append({
            "model": name,
            "file": filename,
            "direction": direction,
            "timeframe": timeframe,
            "balance": round(balance, 2),
            "mae": round(mae, 4),
            "r2": round(r2, 4)
        })

        balance_curves[(direction, timeframe)][name] = curve

# Visualization
for (direction, timeframe), model_curves in balance_curves.items():
    plt.figure(figsize=(10, 6))
    plt.title(f"Balance Evolution — {direction.upper()} {timeframe}")

    for model_name, curve in model_curves.items():
        plt.plot(curve, label=model_name)

    plt.xlabel("Test Sample Index")
    plt.ylabel("Balance ($)")
    plt.legend(loc="upper left")
    plt.tight_layout()
    plt.show()

# Final summary printout
print("\n Final Model Rankings by Ending Balance:")
grouped = defaultdict(list)
for r in results:
    key = (r["direction"], r["timeframe"])
    grouped[key].append(r)

for (direction, timeframe), group in grouped.items():
    print()
    print(f"\n {direction.upper()} {timeframe}")
    for r in sorted(group, key=lambda x: x["balance"], reverse=True):
        print(f"  {r['model']}: Balance ${r['balance']} | MAE {r['mae']} | R² {r['r2']}")
        print()