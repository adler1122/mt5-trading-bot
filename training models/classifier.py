import pandas as pd
import os
import joblib
from collections import defaultdict
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier

# Inputs
symbol = input("Enter symbol (e.g., eurusd): ").lower()
pattern = input("Enter pattern (e.g., fvg): ").lower()
base_path = f"ml datasets/{symbol}/{pattern}"

# Models to test
models = {
    "RandomForest": RandomForestClassifier(),
    "GradientBoosting": GradientBoostingClassifier(),
    "LogisticRegression": LogisticRegression(max_iter=1000),
    "KNN": KNeighborsClassifier(),
    "SVC": SVC(probability=True),
    "XGBoost": XGBClassifier(use_label_encoder=False, eval_metric="logloss")
}

# Store results
results = defaultdict(list)

for filename in os.listdir(base_path):
    if not filename.endswith(".csv"):
        continue

    path = os.path.join(base_path, filename)
    df = pd.read_csv(path)

    if "target" not in df.columns :
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

    # Count total positives and negatives
    total_pos = sum(y_test == 1)
    total_neg = sum(y_test == 0)

    best_score = -1
    best_model = None
    best_name = None
    accurate_found = False

    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        tp = sum((preds == 1) & (y_test == 1))
        tn = sum((preds == 0) & (y_test == 0))

        score = 0
        if total_pos > 0 and total_neg > 0:
            score = (tp / total_pos) * (tn / total_neg)
            #score= (tp / total_pos) + (tn / total_neg)  
        #if score >= 1.0:
        print(f"{filename} — {name}: TP={tp}, TN={tn}, Score={round(score, 4)}")

        results[(direction, timeframe)].append({
            "model": name,
            "score": round(score, 4),
            "tp": tp,
            "tn": tn
        })

        if score > 0.25 :
            accurate_found = True
            if score > best_score:
                best_score = score
                best_model = model
                best_name = name

    # Save best model only if accurate
    if accurate_found and best_model:
        model_filename = f"{symbol}_{pattern}_{direction}_{timeframe}_{best_name}.pkl"
        joblib.dump(best_model, model_filename)
        print(f" Saved best model: {model_filename}")
    else:
        print(f"No accurate model found for {direction.upper()} {timeframe}")