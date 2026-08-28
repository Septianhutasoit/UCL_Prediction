# Model Evaluation Report — ChampIntel XGBoost (Rolling 5 Form & True Elo)

## 1. Overview Dataset & Temporal Split
- **Total Sampel:** 25,979 baris pertandingan historis.
- **Training Set (Masa Lalu):** 20,783 laga.
- **Test Set (Masa Depan):** 5,196 laga.
- **Total Klub Terprofilkan:** 296 klub Eropa.
- **Fitur (8):** match_leg, home_rolling_scored_5, home_rolling_conceded_5, away_rolling_scored_5, away_rolling_conceded_5, form_points_diff_5, elo_difference, aggregate_difference.

## 2. Metrik Evaluasi Model (Temporal Test Set)
| Metrik Evaluasi | Nilai | Penjelasan Akademis |
| :--- | :--- | :--- |
| **Accuracy** | `50.29%` | Persentase ketepatan tebakan kelas hasil laga |
| **Log Loss** | `1.0022` | Mengukur tingkat keyakinan probabilitas (makin kecil makin baik) |
| **Brier Score** | `0.5992` | Mengukur kalibrasi kesalahan prediksi persentase |
| **Macro F1-Score** | `0.3612` | Keseimbangan performa model pada kelas minoritas (Draw) |
