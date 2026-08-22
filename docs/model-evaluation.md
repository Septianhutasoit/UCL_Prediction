# Model Evaluation Report — ChampIntel XGBoost (True Elo)

## 1. Overview Dataset & Temporal Split
- **Total Sampel:** 25,979 baris pertandingan historis.
- **Training Set (Masa Lalu):** 20,783 laga.
- **Test Set (Masa Depan):** 5,196 laga.
- **Total Klub Terprofilkan (True Elo):** 296 klub.
- **Fitur (7):** match_leg, home_avg_scored, home_avg_conceded, away_avg_scored, away_avg_conceded, elo_difference, aggregate_difference — dihitung via `ml/features/feature_builder.py`,
  dipakai identik oleh training dan `predictor.py` saat live inference (anti feature-drift).
- **Catatan Elo:** rating awal semua tim 1500.0, di-update per laga secara walk-forward
  (K-factor + margin-of-victory multiplier + home advantage), bukan angka statis.

## 2. Metrik Evaluasi Model (Temporal Test Set)
| Metrik Evaluasi | Nilai | Penjelasan Akademis |
| :--- | :--- | :--- |
| **Accuracy** | `50.33%` | Persentase ketepatan tebakan kelas hasil laga |
| **Log Loss** | `0.9963` | Mengukur tingkat keyakinan probabilitas (makin kecil makin baik) |
| **Brier Score** | `0.5950` | Mengukur kalibrasi kesalahan prediksi persentase (makin mendekati 0 makin sempurna) |
| **Macro F1-Score** | `0.3630` | Menilai keseimbangan performa model pada kelas minoritas (Draw) |

## 3. Validasi Anti Data-Leakage & Anti Feature-Drift
Fitur dihitung secara *walk-forward* (state Elo & rata-rata gol tim di-update
SETELAH, bukan sebelum, fitur laga tersebut dihitung) melalui `feature_builder.py`,
dan file yang sama persis dipanggil oleh `predictor.py` saat inference.
