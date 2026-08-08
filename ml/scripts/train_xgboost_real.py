import os
import json
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def main():
    raw_path = os.path.join("..", "datasets", "raw", "matches.csv")
    model_dir = os.path.join("..", "models")
    
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    df = pd.read_csv(raw_path)
    df.columns = df.columns.str.strip()

    # Mapping Target
    result_mapping = {"Away Win": 0, "Draw": 1, "Home Win": 2}
    df["target"] = df["result"].map(result_mapping)
    df = df.dropna(subset=['target', 'home_team', 'away_team', 'home_goals', 'away_goals'])

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).sort_values('date').reset_index(drop=True)

    # Feature Engineering (Statistik Historis Dinamis)
    team_scored, team_conceded, team_matches = {}, {}, {}
    home_avg_scored, away_avg_scored = [], []
    home_avg_conceded, away_avg_conceded = [], []

    for idx, row in df.iterrows():
        ht, at = row['home_team'], row['away_team']
        hg, ag = row['home_goals'], row['away_goals']

        h_scored = team_scored.get(ht, 1.0) / max(1, team_matches.get(ht, 1))
        h_conceded = team_conceded.get(ht, 1.0) / max(1, team_matches.get(ht, 1))
        a_scored = team_scored.get(at, 1.0) / max(1, team_matches.get(at, 1))
        a_conceded = team_conceded.get(at, 1.0) / max(1, team_matches.get(at, 1))

        home_avg_scored.append(h_scored)
        home_avg_conceded.append(h_conceded)
        away_avg_scored.append(a_scored)
        away_avg_conceded.append(a_conceded)

        team_scored[ht] = team_scored.get(ht, 0.0) + hg
        team_conceded[ht] = team_conceded.get(ht, 0.0) + ag
        team_matches[ht] = team_matches.get(ht, 0) + 1

        team_scored[at] = team_scored.get(at, 0.0) + ag
        team_conceded[at] = team_conceded.get(at, 0.0) + hg
        team_matches[at] = team_matches.get(at, 0) + 1

    df['home_avg_scored'] = home_avg_scored
    df['home_avg_conceded'] = home_avg_conceded
    df['away_avg_scored'] = away_avg_scored
    df['away_avg_conceded'] = away_avg_conceded
    df['match_leg'] = 1
    df['elo_difference'] = 0.0

    # FITUR TANPA KEBOCORAN DATA
    feature_columns = [
        "match_leg",
        "home_avg_scored",
        "home_avg_conceded",
        "away_avg_scored",
        "away_avg_conceded",
        "elo_difference"
    ]

    X = df[feature_columns]
    y = df["target"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("🚀 Melatih ulang model XGBoost secara adil (tanpa data kebocoran)...")
    model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        max_depth=4,
        learning_rate=0.03,
        n_estimators=100,
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"🎯 Akurasi model realistis pada data uji: {acc * 100:.2f}%")

    # Simpan model & metadata
    model_path = os.path.join(model_dir, "xgboost_ucl.json")
    meta_path = os.path.join(model_dir, "feature_columns.json")
    
    model.save_model(model_path)
    with open(meta_path, "w") as f:
        json.dump(feature_columns, f)

    print("📁 Model realistis baru berhasil disimpan!")

if __name__ == "__main__":
    main()