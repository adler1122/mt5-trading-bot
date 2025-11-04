import pandas as pd

# Load dataset
symbol=input("symbol: ")

df = pd.read_csv(f"datasets/cleaned_{symbol}_H1.csv")

# Convert time_only to integer hour
df["hour_int"] = pd.to_datetime(df["time_only"], format="%H:%M:%S").dt.hour

# Sort by date and hour
df = df.sort_values(by=["date", "hour_int"])

# Filter noisy days
noisy_df = df[df["noisy_day"] == True].copy()
noisy_dates = sorted(noisy_df["date"].unique())
if len(noisy_dates) > 2:
    noisy_df = noisy_df[~noisy_df["date"].isin([noisy_dates[0], noisy_dates[-1]])]
counts = noisy_df.groupby("date").size()
valid_noisy_dates = counts[counts == 23].index
noisy_df = noisy_df[noisy_df["date"].isin(valid_noisy_dates)]

# Filter clean days
clean_df = df[df["noisy_day"] == False].copy()
clean_dates = sorted(clean_df["date"].unique())
if len(clean_dates) > 2:
    clean_df = clean_df[~clean_df["date"].isin([clean_dates[0], clean_dates[-1]])]
counts = clean_df.groupby("date").size()
valid_clean_dates = counts[counts == 23].index
clean_df = clean_df[clean_df["date"].isin(valid_clean_dates)]

# Loop through first 6 hours
print("Hour | Best i | Threshold | Score")

for hour in range(6):
    
    # Cumulative volume for noisy days
    noisy_cum = []
    for date in noisy_df["date"].unique():
        day_df = noisy_df[noisy_df["date"] == date]
        vol_sum = day_df[day_df["hour_int"] <= hour]["tick_volume"].sum()
        noisy_cum.append(vol_sum)

    # Cumulative volume for clean days
    clean_cum = []
    for date in clean_df["date"].unique():
        day_df = clean_df[clean_df["date"] == date]
        vol_sum = day_df[day_df["hour_int"] <= hour]["tick_volume"].sum()
        clean_cum.append(vol_sum)

    # Compute stats from noisy days
    q1 = pd.Series(noisy_cum).quantile(0.25)
    q3 = pd.Series(noisy_cum).quantile(0.75)
    iqr = q3 - q1
    mean = pd.Series(noisy_cum).mean()

    best_i = None
    best_score = -1
    best_threshold = None

    for i in [0.25, 0.5, 0.75, 1, 1.25, 1.5]:
        threshold = mean - i * iqr

        # True positives: noisy days above threshold
        tp = sum(v >= threshold for v in noisy_cum)
        total_noisy = len(noisy_cum)

        # True negatives: clean days below threshold
        tn = sum(v < threshold for v in clean_cum)
        total_clean = len(clean_cum)

        score = (tp / total_noisy) * (tn / total_clean)

        if score > best_score:
            best_score = score
            best_i = i
            best_threshold = threshold

    print(f"{hour+1:>4} | {best_i:<6} | {best_threshold:>9.2f} | {best_score:.4f}")