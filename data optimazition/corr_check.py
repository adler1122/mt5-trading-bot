import pandas as pd
import os
from sklearn.feature_selection import mutual_info_classif
from sklearn.preprocessing import LabelEncoder

# Inputs
pattern = input("Enter pattern name (e.g., fvg, orderblock): ").lower()
symbol = input("Enter symbol (e.g., xauusd): ").lower()
base_path = f"ml datasets/{symbol}/{pattern}"

# Loop through all CSVs in the pattern folder
for filename in os.listdir(base_path):
    if not filename.endswith(".csv"):
        continue

    path = os.path.join(base_path, filename)
    df = pd.read_csv(path)

    if "target" not in df.columns:
        print(f"Skipping {filename} — no 'target' column")
        continue

    # Separate features
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.drop("target", errors="ignore")
    categorical_cols = df.select_dtypes(include=["object", "bool", "category"]).columns

    # --- Numeric correlation ---
    corr = df[numeric_cols].corrwith(df["target"]).abs()
    low_corr = corr[corr < 0.01].index.tolist()

    # --- Categorical mutual information ---
    mi_scores = {}
    for col in categorical_cols:
        try:
            le = LabelEncoder()
            encoded = le.fit_transform(df[col].astype(str))
            mi = mutual_info_classif(encoded.reshape(-1, 1), df["target"], discrete_features=True)
            if mi[0] < 0.01:
                mi_scores[col] = mi[0]
        except Exception as e:
            print(f"Skipping MI for {col} in {filename}: {e}")

    # Drop low-signal features
    to_drop = low_corr + list(mi_scores.keys())
    df.drop(columns=to_drop, inplace=True, errors="ignore")

    # Save in-place
    df.to_csv(path, index=False)
    print(f"Processed {filename} — dropped: {to_drop}")