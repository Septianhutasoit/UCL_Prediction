import os
import sys
import json
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import accuracy_score, log_loss, f1_score

# --- Hubungkan ke ml/features/feature_builder.py (letaknya folder tetangga, bukan sejajar) ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.dirname(SCRIPT_DIR)  # naik satu folder: ml/scripts -> ml
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

    print("🛠️ Menghitung fitur via feature_builder.py (True Elo + rata-rata gol semusim)...")

    # State kumulatif yang di-update sambil jalan (walk-forward, anti data-leakage)
    team_elo = {}
    team_scored, team_conceded, team_matches = {}, {}, {}

    feature_rows = []

    for _, row in df.iterrows():
        ht, at = row["home_team"], row["away_team"]
        hg, ag = row["home_goals"], row["away_goals"]
        res = row["result"]

        h_elo = team_elo.get(ht, INITIAL_ELO)
        a_elo = team_elo.get(at, INITIAL_ELO)

        h_matches = max(1, team_matches.get(ht, 1))
        a_matches = max(1, team_matches.get(at, 1))
        h_avg_scored = team_scored.get(ht, 1.0) / h_matches
        h_avg_conceded = team_conceded.get(ht, 1.0) / h_matches
        a_avg_scored = team_scored.get(at, 1.0) / a_matches
        a_avg_conceded = team_conceded.get(at, 1.0) / a_matches

        # 1. Hitung fitur DULU pakai state SEBELUM laga ini (mencegah data-leakage)
        #    Data historis semuanya Leg 1 -> aggregate_difference otomatis 0.0, itu wajar.
        feat_array = extract_match_features(
            match_leg=1,
            home_rolling_scored=h_avg_scored,
            home_rolling_conceded=h_avg_conceded,
            away_rolling_scored=a_avg_scored,
            away_rolling_conceded=a_avg_conceded,
            home_elo=h_elo,
            away_elo=a_elo,
            home_leg1_score=0,
            away_leg1_score=0,
        )
        feature_rows.append(feat_array[0])

        # 2. BARU update state dengan hasil laga ini
        goal_diff = int(hg - ag)
        new_h_elo, new_a_elo = update_elo(h_elo, a_elo, res, goal_diff)
        team_elo[ht] = new_h_elo
        team_elo[at] = new_a_elo

        team_scored[ht] = team_scored.get(ht, 0.0) + hg
        team_conceded[ht] = team_conceded.get(ht, 0.0) + ag
        team_matches[ht] = team_matches.get(ht, 0) + 1

        team_scored[at] = team_scored.get(at, 0.0) + ag
        team_conceded[at] = team_conceded.get(at, 0.0) + hg
        team_matches[at] = team_matches.get(at, 0) + 1

    features_df = pd.DataFrame(feature_rows, columns=FEATURE_COLUMN_NAMES)
    for col in FEATURE_COLUMN_NAMES:
        df[col] = features_df[col].values

    X = df[FEATURE_COLUMN_NAMES]
    y = df["target"].astype(int)

    # Temporal split: 80% laga masa lalu untuk train, 20% laga terbaru untuk test
    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    print(f"🚀 Melatih model XGBoost pada {len(X_train):,} laga masa lalu ({len(FEATURE_COLUMN_NAMES)} fitur)...")
    model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        max_depth=5,
        learning_rate=0.05,
        n_estimators=100,
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

    # --- Susun team_stats.json final: SEKARANG termasuk elo_rating (dibutuhkan predictor.py) ---
    team_stats = {}
    for team in set(list(team_elo.keys())):
        matches = max(1, team_matches.get(team, 1))
        team_stats[team] = {
            "elo_rating": round(float(team_elo.get(team, INITIAL_ELO)), 1),
            "avg_scored": round(float(team_scored.get(team, 1.0) / matches), 2),
            "avg_conceded": round(float(team_conceded.get(team, 1.0) / matches), 2),
            "matches_played": int(team_matches.get(team, 0)),
        }

    eval_report = f"""# Model Evaluation Report — ChampIntel XGBoost (True Elo)

## 1. Overview Dataset & Temporal Split
- **Total Sampel:** {len(df):,} baris pertandingan historis.
- **Training Set (Masa Lalu):** {len(X_train):,} laga.
- **Test Set (Masa Depan):** {len(X_test):,} laga.
- **Total Klub Terprofilkan (True Elo):** {len(team_stats):,} klub.
- **Fitur ({len(FEATURE_COLUMN_NAMES)}):** {", ".join(FEATURE_COLUMN_NAMES)} — dihitung via `ml/features/feature_builder.py`,
  dipakai identik oleh training dan `predictor.py` saat live inference (anti feature-drift).
- **Catatan Elo:** rating awal semua tim {INITIAL_ELO}, di-update per laga secara walk-forward
  (K-factor + margin-of-victory multiplier + home advantage), bukan angka statis.

## 2. Metrik Evaluasi Model (Temporal Test Set)
| Metrik Evaluasi | Nilai | Penjelasan Akademis |
| :--- | :--- | :--- |
| **Accuracy** | `{acc * 100:.2f}%` | Persentase ketepatan tebakan kelas hasil laga |
| **Log Loss** | `{loss:.4f}` | Mengukur tingkat keyakinan probabilitas (makin kecil makin baik) |
| **Brier Score** | `{brier:.4f}` | Mengukur kalibrasi kesalahan prediksi persentase (makin mendekati 0 makin sempurna) |
| **Macro F1-Score** | `{f1:.4f}` | Menilai keseimbangan performa model pada kelas minoritas (Draw) |

## 3. Validasi Anti Data-Leakage & Anti Feature-Drift
Fitur dihitung secara *walk-forward* (state Elo & rata-rata gol tim di-update
SETELAH, bukan sebelum, fitur laga tersebut dihitung) melalui `feature_builder.py`,
dan file yang sama persis dipanggil oleh `predictor.py` saat inference.
"""
    report_path = os.path.join(docs_dir, "model-evaluation.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(eval_report)

    model.save_model(os.path.join(model_dir, "xgboost_ucl.json"))
    with open(os.path.join(model_dir, "feature_columns.json"), "w") as f:
        json.dump(FEATURE_COLUMN_NAMES, f)
    with open(os.path.join(model_dir, "team_stats.json"), "w") as f:
        json.dump(team_stats, f, indent=4)

    print(f"📁 Model & Profil {len(team_stats)} Tim (dengan True Elo) berhasil disimpan di ml/models/!")
    print(f"📄 Laporan evaluasi otomatis tersimpan di: {report_path}")


if __name__ == "__main__":
    main()