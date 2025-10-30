import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

# Inputs
symbol = input("Enter symbol (e.g., xauusd): ").lower()
base_path = f"ml datasets/{symbol}/fvg"
scaler_path = "scalers"

# Models to test
models = {
    "RandomForest": RandomForestClassifier(),
    "GradientBoosting": GradientBoostingClassifier(),
    "LogisticRegression": LogisticRegression(max_iter=1000),
    "KNN": KNeighborsClassifier(),
    "SVC": SVC(probability=True),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric="logloss")
}

# Store results and balance curves
results = []
balance_curves = defaultdict(lambda: defaultdict(list))  # {(direction, timeframe): {model: [balance]}}

for filename in os.listdir(base_path):
    if not filename.endswith(".csv"):
        continue

    path = os.path.join(base_path, filename)
    df = pd.read_csv(path)

    if "target" not in df.columns or "gap_size" not in df.columns:
        continue

    # Extract direction and timeframe
    parts = filename.replace(".csv", "").split("_")
    if len(parts) < 4:
        print(f"Skipping malformed filename: {filename}")
        continue
    direction = parts[1]
    timeframe = parts[-1]

    # Load scaler
    scaler_name = f"scaler_{symbol}_fvg_{direction}_{timeframe}.pkl"
    scaler_path_full = os.path.join(scaler_path, scaler_name)
    if not os.path.exists(scaler_path_full):
        print(f"Missing scaler for {filename}")
        continue
    scaler = joblib.load(scaler_path_full)

    # Unscale gap_size manually
    try:
        gap_index = list(scaler.feature_names_in_).index("gap_size")
        gap_min = scaler.data_min_[gap_index]
        gap_max = scaler.data_max_[gap_index]
        gap_scaled = df["gap_size"].values
        gap_unscaled = gap_scaled * (gap_max - gap_min) + gap_min
    except Exception as e:
        print(f"Error unscaling gap_size in {filename}: {e}")
        continue

    # Split data
    split_idx = int(len(df) * 0.9)
    X = df.drop(columns=["target"])
    y = df["target"]

    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    gap_test = gap_unscaled[split_idx:]

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        # Evaluation
        balance = 1000
        curve = []
        for pred, true, gap in zip(preds, y_test, gap_test):
            delta = gap * 10
            balance += delta if pred == true else -delta
            curve.append(balance)

        f1 = f1_score(y_test, preds)
        acc = accuracy_score(y_test, preds)

        results.append({
            "model": name,
            "file": filename,
            "direction": direction,
            "timeframe": timeframe,
            "balance": round(balance, 2),
            "f1": round(f1, 4),
            "accuracy": round(acc, 4)
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
    print(f"\n {direction.upper()} {timeframe}")
    print("")
    print("")
    for r in sorted(group, key=lambda x: x["balance"], reverse=True):
        print(f"  {r['model']}: Balance ${r['balance']} | Accuracy {r['accuracy']} | F1 {r['f1']}")
        print("")