import os
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import json

def train_model():
    # 1. Path dataset dan direktori simpan model
    dataset_path = os.path.join("..", "datasets", "sample", "sample_matches.csv")
    model_dir = os.path.join("..", "models")
    
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)

    print("Memuat dataset...")
    df = pd.read_csv(dataset_path)

    # 2. Tentukan fitur (X) dan target (y)
    feature_columns = [
        "match_leg",
        "home_win_rate", "away_win_rate",
        "home_form_points_last_5", "away_form_points_last_5",
        "home_goals_per_match", "away_goals_per_match",
        "home_goals_conceded_per_match", "away_goals_conceded_per_match",
        "home_xg_last_5", "away_xg_last_5",
        "home_xga_last_5", "away_xga_last_5",
        "elo_difference", "rest_days_difference",
        "home_aggregate_before", "away_aggregate_before", "aggregate_difference"
    ]

    X = df[feature_columns]
    y = df["target"]

    # 3. Bagi data untuk training dan testing
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

    print("Melatih model XGBoost...")
    # Menggunakan multi:softprob untuk menghasilkan probabilitas 3 kelas (Away Win, Draw, Home Win)
    model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        max_depth=3,
        learning_rate=0.1,
        n_estimators=50,
        random_state=42
    )

    model.fit(X_train, y_train)

    # 4. Evaluasi sederhana
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Model berhasil dilatih! Akurasi pada data uji: {acc * 100:.2f}%")

    # 5. Simpan model dalam format JSON (standar XGBoost)
    model_path = os.path.join(model_dir, "xgboost_ucl.json")
    model.save_model(model_path)
    print(f"Model berhasil disimpan di: {model_path}")

    # Simpan juga daftar kolom fitur agar nanti FastAPI tahu urutan inputnya
    meta_path = os.path.join(model_dir, "feature_columns.json")
    with open(meta_path, "w") as f:
        json.dump(feature_columns, f)
    print(f"Metadata fitur disimpan di: {meta_path}")

if __name__ == "__main__":
    train_model()