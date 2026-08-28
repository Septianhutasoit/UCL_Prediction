import os
import sys
import json
from collections import deque, defaultdict
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, log_loss, f1_score

# Hubungkan ke ml/features/feature_builder.py
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(ML_DIR)

from features.feature_builder import (
    extract_match_features,
    update_elo,
    INITIAL_ELO,
    FEATURE_COLUMN_NAMES,
)


def multiclass_brier_score(y_true, y_prob):
    """Menghitung Brier Score untuk klasifikasi multi-kelas (0, 1, 2)."""
    n_samples = len(y_true)
    y_true_onehot = np.zeros((n_samples, 3))
    y_true_onehot[np.arange(n_samples), y_true] = 1
    return np.mean(np.sum((y_prob - y_true_onehot) ** 2, axis=1))


def main():
    raw_path = os.path.join("..", "datasets", "raw", "matches.csv")
    model_dir = os.path.join("..", "models")
    docs_dir = os.path.join("..", "..", "docs")

    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)

    print(f"Memuat dataset dari: {raw_path}")
    df = pd.read_csv(raw_path)
    df.columns = df.columns.str.strip()

    result_mapping = {"Away Win": 0, "Draw": 1, "Home Win": 2}
    df["target"] = df["result"].map(result_mapping)
    df = df.dropna(subset=["target", "home_team", "away_team", "home_goals", "away_goals"])

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

    print("🛠️ Menghitung fitur via feature_builder.py (True Elo + Rolling 5-Match Form)...")

    # 1. State Antrean 5 Laga Terakhir (Rolling Window) + True Elo
    team_elo = {}
    team_goals_scored_5 = defaultdict(lambda: deque(maxlen=5))
    team_goals_conceded_5 = defaultdict(lambda: deque(maxlen=5))
    team_pts_5 = defaultdict(lambda: deque(maxlen=5))
    team_matches = defaultdict(int)

    feature_rows = []

    for _, row in df.iterrows():
        ht, at = row["home_team"], row["away_team"]
        hg, ag = int(row["home_goals"]), int(row["away_goals"])
        res = row["result"]

        h_elo = team_elo.get(ht, INITIAL_ELO)
        a_elo = team_elo.get(at, INITIAL_ELO)

        # 2. Hitung performa momentum 5 laga sebelum laga ini (Anti-Leakage)
        h_sc_5 = np.mean(team_goals_scored_5[ht]) if len(team_goals_scored_5[ht]) > 0 else 1.4
        h_cc_5 = np.mean(team_goals_conceded_5[ht]) if len(team_goals_conceded_5[ht]) > 0 else 1.2
        a_sc_5 = np.mean(team_goals_scored_5[at]) if len(team_goals_scored_5[at]) > 0 else 1.2
        a_cc_5 = np.mean(team_goals_conceded_5[at]) if len(team_goals_conceded_5[at]) > 0 else 1.3

        h_pts_5 = np.sum(team_pts_5[ht]) if len(team_pts_5[ht]) > 0 else 7.0
        a_pts_5 = np.sum(team_pts_5[at]) if len(team_pts_5[at]) > 0 else 6.0

        # Ekstraksi fitur via feature_builder terpadu
        feat_array = extract_match_features(
            match_leg=1,
            home_rolling_scored_5=h_sc_5,
            home_rolling_conceded_5=h_cc_5,
            away_rolling_scored_5=a_sc_5,
            away_rolling_conceded_5=a_cc_5,
            home_form_pts_5=h_pts_5,
            away_form_pts_5=a_pts_5,
            home_elo=h_elo,
            away_elo=a_elo,
            home_leg1_score=0,
            away_leg1_score=0,
        )
        feature_rows.append(feat_array[0])

        # 3. Update True Elo dan Antrean 5 Laga setelah laga selesai
        goal_diff = hg - ag
        new_h_elo, new_a_elo = update_elo(h_elo, a_elo, res, goal_diff)
        team_elo[ht] = new_h_elo
        team_elo[at] = new_a_elo

        team_goals_scored_5[ht].append(hg)
        team_goals_conceded_5[ht].append(ag)
        team_goals_scored_5[at].append(ag)
        team_goals_conceded_5[at].append(hg)

        h_pt = 3 if res == "Home Win" else (1 if res == "Draw" else 0)
        a_pt = 3 if res == "Away Win" else (1 if res == "Draw" else 0)
        team_pts_5[ht].append(h_pt)
        team_pts_5[at].append(a_pt)
        team_matches[ht] += 1
        team_matches[at] += 1

    features_df = pd.DataFrame(feature_rows, columns=FEATURE_COLUMN_NAMES)
    for col in FEATURE_COLUMN_NAMES:
        df[col] = features_df[col].values

    X = df[FEATURE_COLUMN_NAMES]
    y = df["target"].astype(int)

    # 4. Temporal Split (80% Masa Lalu untuk Train, 20% Masa Depan untuk Test)
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print(f"🚀 Melatih model XGBoost pada {len(X_train):,} laga ({len(FEATURE_COLUMN_NAMES)} fitur)...")
    model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        max_depth=5,
        learning_rate=0.04,
        n_estimators=120,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)

    acc = accuracy_score(y_test, preds)
    loss = log_loss(y_test, probs)
    brier = multiclass_brier_score(y_test.values, probs)
    f1 = f1_score(y_test, preds, average="macro")

    print(f"🎯 Akurasi (Accuracy): {acc * 100:.2f}%")
    print(f"📉 Log Loss: {loss:.4f} | 📐 Brier Score: {brier:.4f} | 📊 F1-Score: {f1:.4f}")

    # 5. Susun team_stats.json dengan data Elo & Form 5 Laga
    team_stats = {}
    for team, elo in team_elo.items():
        team_stats[team] = {
            "elo_rating": round(float(elo), 1),
            "avg_scored_5": round(float(np.mean(team_goals_scored_5[team])), 2) if len(team_goals_scored_5[team]) > 0 else 1.4,
            "avg_conceded_5": round(float(np.mean(team_goals_conceded_5[team])), 2) if len(team_goals_conceded_5[team]) > 0 else 1.2,
            "form_pts_5": int(np.sum(team_pts_5[team])) if len(team_pts_5[team]) > 0 else 7,
            "matches_played": int(team_matches[team]),
        }

    # Simpan Laporan Evaluasi
    eval_report = f"""# Model Evaluation Report — ChampIntel XGBoost (Rolling 5 Form & True Elo)

## 1. Overview Dataset & Temporal Split
- **Total Sampel:** {len(df):,} baris pertandingan historis.
- **Training Set (Masa Lalu):** {len(X_train):,} laga.
- **Test Set (Masa Depan):** {len(X_test):,} laga.
- **Total Klub Terprofilkan:** {len(team_stats):,} klub Eropa.
- **Fitur ({len(FEATURE_COLUMN_NAMES)}):** {", ".join(FEATURE_COLUMN_NAMES)}.

## 2. Metrik Evaluasi Model (Temporal Test Set)
| Metrik Evaluasi | Nilai | Penjelasan Akademis |
| :--- | :--- | :--- |
| **Accuracy** | `{acc * 100:.2f}%` | Persentase ketepatan tebakan kelas hasil laga |
| **Log Loss** | `{loss:.4f}` | Mengukur tingkat keyakinan probabilitas (makin kecil makin baik) |
| **Brier Score** | `{brier:.4f}` | Mengukur kalibrasi kesalahan prediksi persentase |
| **Macro F1-Score** | `{f1:.4f}` | Keseimbangan performa model pada kelas minoritas (Draw) |
"""
    with open(os.path.join(docs_dir, "model-evaluation.md"), "w", encoding="utf-8") as f:
        f.write(eval_report)

    model.save_model(os.path.join(model_dir, "xgboost_ucl.json"))
    with open(os.path.join(model_dir, "feature_columns.json"), "w") as f:
        json.dump(FEATURE_COLUMN_NAMES, f)
    with open(os.path.join(model_dir, "team_stats.json"), "w") as f:
        json.dump(team_stats, f, indent=4)

      # Simpan metrik resmi ke model_metrics.json (untuk dibaca dinamis oleh Agent)
        metrics_data = {
            "training_samples": len(X_train),
            "test_samples": len(X_test),
            "total_samples": len(df),
            "accuracy": f"{acc * 100:.2f}%",
            "log_loss": round(float(loss), 4),
            "brier_score": round(float(brier), 4),
            "f1_score": round(float(f1), 4),
            "validation_method": "Temporal Split (Anti Data-Leakage)",
            "calibration_status": "Well-Calibrated (Brier < 0.60)" if brier < 0.60 else "Moderate"
        }
        with open(os.path.join(model_dir, "model_metrics.json"), "w") as f:
            json.dump(metrics_data, f, indent=4)

    print(f"📁 Model & Profil {len(team_stats)} Tim (dengan Form 5 Laga) berhasil disimpan!")


if __name__ == "__main__":
    main()