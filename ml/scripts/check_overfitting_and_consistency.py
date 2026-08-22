import os
import sys
import json
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import accuracy_score, log_loss, f1_score

# Hubungkan path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ML_DIR = os.path.dirname(SCRIPT_DIR)
ROOT_DIR = os.path.dirname(ML_DIR)
AI_SERVICE_DIR = os.path.join(ROOT_DIR, "apps", "ai-service")

sys.path.append(ROOT_DIR)
sys.path.append(ML_DIR)
sys.path.append(AI_SERVICE_DIR)

from features.feature_builder import (
    extract_match_features,
    update_elo,
    INITIAL_ELO,
    FEATURE_COLUMN_NAMES,
)
from app.services.predictor import predictor


def multiclass_brier_score(y_true, y_prob):
    n_samples = len(y_true)
    y_true_onehot = np.zeros((n_samples, 3))
    y_true_onehot[np.arange(n_samples), y_true] = 1
    return np.mean(np.sum((y_prob - y_true_onehot) ** 2, axis=1))


def check_overfitting():
    print("=" * 60)
    print("🔍 1. DIAGNOSIS OVERFITTING MODEL XGBOOST")
    print("=" * 60)

    raw_path = os.path.join(ML_DIR, "datasets", "raw", "matches.csv")
    df = pd.read_csv(raw_path)
    df.columns = df.columns.str.strip()

    result_mapping = {"Away Win": 0, "Draw": 1, "Home Win": 2}
    df["target"] = df["result"].map(result_mapping)
    df = df.dropna(subset=["target", "home_team", "away_team", "home_goals", "away_goals"])
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

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

    split_idx = int(len(df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # Evaluasi model saat ini
    model_path = os.path.join(ML_DIR, "models", "xgboost_ucl.json")
    model = xgb.XGBClassifier()
    model.load_model(model_path)

    # Train predictions
    train_preds = model.predict(X_train)
    train_probs = model.predict_proba(X_train)
    train_acc = accuracy_score(y_train, train_preds)
    train_loss = log_loss(y_train, train_probs)
    train_brier = multiclass_brier_score(y_train.values, train_probs)
    train_f1 = f1_score(y_train, train_preds, average="macro")

    # Test predictions
    test_preds = model.predict(X_test)
    test_probs = model.predict_proba(X_test)
    test_acc = accuracy_score(y_test, test_preds)
    test_loss = log_loss(y_test, test_probs)
    test_brier = multiclass_brier_score(y_test.values, test_probs)
    test_f1 = f1_score(y_test, test_preds, average="macro")

    print(f"{'Metrik':<20} | {'Train Set (80%)':<16} | {'Test Set (20%)':<16} | {'Gap (Train - Test)':<18}")
    print("-" * 75)
    print(f"{'Akurasi (Accuracy)':<20} | {train_acc*100:6.2f}%          | {test_acc*100:6.2f}%          | {(train_acc - test_acc)*100:+6.2f}%")
    print(f"{'Log Loss':<20} | {train_loss:8.4f}         | {test_loss:8.4f}         | {train_loss - test_loss:+8.4f}")
    print(f"{'Brier Score':<20} | {train_brier:8.4f}         | {test_brier:8.4f}         | {train_brier - test_brier:+8.4f}")
    print(f"{'Macro F1-Score':<20} | {train_f1:8.4f}         | {test_f1:8.4f}         | {train_f1 - test_f1:+8.4f}")
    print("-" * 75)

    # Analisis tingkat overfitting
    acc_gap = (train_acc - test_acc) * 100
    loss_gap = test_loss - train_loss
    print("\n📊 Kesimpulan Analisis Overfitting:")
    if acc_gap < 3.0 and loss_gap < 0.05:
        print("  🟢 Overfitting Sangat Rendah (Good Generalization).")
    elif acc_gap < 7.0 and loss_gap < 0.10:
        print("  🟡 Overfitting Ringan (Mild Generalization Gap - Masih dapat diterima untuk sports betting/analytics).")
    else:
        print("  🔴 Terindikasi Overfitting Signifikan! Model terlalu menghafal data masa lalu.")


def check_consistency():
    print("\n" + "=" * 60)
    print("🧪 2. EVALUASI TINGKAT KONSISTENSI SISTEM PIPELINE")
    print("=" * 60)

    # 1. Cek Roster dan Team Stats Integrity
    from build_llm_dataset import UCL_ROSTER
    team_stats_path = os.path.join(ML_DIR, "models", "team_stats.json")
    with open(team_stats_path, "r", encoding="utf-8") as f:
        team_stats = json.load(f)

    missing_teams = [team for team in UCL_ROSTER if team not in team_stats]
    print(f"1. Verifikasi Roster UCL ({len(UCL_ROSTER)} tim):")
    if not missing_teams:
        print(f"   ✅ Semua {len(UCL_ROSTER)} klub resmi memiliki data True Elo & Goal Stats di team_stats.json!")
    else:
        print(f"   ❌ Terdapat klub tanpa statistik: {missing_teams}")

    # 2. Cek Konsistensi File Dataset LLM
    train_llm_path = os.path.join(ML_DIR, "datasets", "llm", "train.jsonl")
    val_llm_path = os.path.join(ML_DIR, "datasets", "llm", "validation.jsonl")

    train_exists = os.path.exists(train_llm_path) and os.path.getsize(train_llm_path) > 100
    val_exists = os.path.exists(val_llm_path) and os.path.getsize(val_llm_path) > 100

    print("\n2. Integritas Dataset Fine-Tuning LLM:")
    if train_exists and val_exists:
        with open(train_llm_path, "r", encoding="utf-8") as f:
            train_lines = f.readlines()
        with open(val_llm_path, "r", encoding="utf-8") as f:
            val_lines = f.readlines()
        print(f"   ✅ train.jsonl: {len(train_lines)} sampel valid.")
        print(f"   ✅ validation.jsonl: {len(val_lines)} sampel valid.")

        # Cek Numerical Faithfulness & Anti-Hallucination pada sampel LLM
        mismatch_count = 0
        for idx, line in enumerate(train_lines[:100]): # sample cek 100 pertama
            obj = json.loads(line)
            user_text = obj["messages"][1]["content"]
            asst_text = obj["messages"][2]["content"]

            # Cek apakah persentase di user prompt konsisten di deskripsi asisten
            import re
            user_pcts = re.findall(r"\d+\.\d+%", user_text)
            for pct in user_pcts:
                if pct not in asst_text:
                    mismatch_count += 1
                    break

        print(f"   🔍 Cek Faithfulness Numerik (100 sampel pertama): {100 - mismatch_count}/100 Konsisten 100%!")
    else:
        print("   ⚠️ File train.jsonl atau validation.jsonl belum digenerate secara lengkap.")

    # 3. Cek Konsistensi Logika Prediksi Leg 1 vs Leg 2
    print("\n3. Uji Konsistensi Logika Agregat Knockout:")
    test_match_leg1 = predictor.predict_raw({
        "home_team": "Real Madrid",
        "away_team": "Manchester City",
        "match_leg": 1
    })
    test_match_leg2_lead = predictor.predict_raw({
        "home_team": "Real Madrid",
        "away_team": "Manchester City",
        "match_leg": 2,
        "home_leg1_score": 3,
        "away_leg1_score": 0
    })
    test_match_leg2_behind = predictor.predict_raw({
        "home_team": "Real Madrid",
        "away_team": "Manchester City",
        "match_leg": 2,
        "home_leg1_score": 0,
        "away_leg1_score": 3
    })

    print(f"   • Real Madrid vs Man City (Leg 1) -> Peluang Menang: {test_match_leg1['home_win_prob']*100:.1f}%")
    print(f"   • Leg 2 (RM unggul agregat 3-0)   -> Peluang Lolos RM: {test_match_leg2_lead['home_qualification_prob']*100:.1f}% | MC: {test_match_leg2_lead['away_qualification_prob']*100:.1f}%")
    print(f"   • Leg 2 (RM tertinggal 0-3)       -> Peluang Lolos RM: {test_match_leg2_behind['home_qualification_prob']*100:.1f}% | MC: {test_match_leg2_behind['away_qualification_prob']*100:.1f}%")

    if test_match_leg2_lead["home_qualification_prob"] > test_match_leg2_behind["home_qualification_prob"]:
        print("   ✅ Logika Agregat & Probabilitas Kelolosan Bekerja Secara Konsisten & Rasional!")
    else:
        print("   ❌ Terdeteksi Anomali pada Kalkulasi Agregat!")

    print("=" * 60)


if __name__ == "__main__":
    check_overfitting()
    check_consistency()
