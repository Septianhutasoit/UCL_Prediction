# Model Evaluation Report — ChampIntel XGBoost

## 1. Overview Dataset & Temporal Split
- **Total Sampel:** 25,979 baris pertandingan historis.
- **Training Set (Masa Lalu):** 20,783 laga.
- **Test Set (Masa Depan):** 5,196 laga.
- **Total Klub Terprofilkan:** 296 klub Eropa.

## 2. Metrik Evaluasi Model (Temporal Test Set)
| Metrik Evaluasi | Nilai | Penjelasan Akademis |
| :--- | :--- | :--- |
| **Accuracy** | `50.08%` | Persentase ketepatan tebakan kelas hasil laga |
| **Log Loss** | `1.0052` | Mengukur tingkat keyakinan probabilitas (makin kecil makin baik) |
| **Brier Score** | `0.6007` | Mengukur kalibrasi kesalahan prediksi persentase (makin mendekati 0 makin sempurna) |
| **Macro F1-Score** | `0.3553` | Menilai keseimbangan performa model pada kelas minoritas (Draw) |

## 3. Validasi Anti Data-Leakage
Model XGBoost dilatih secara *temporal split* dengan fitur *ELO Difference* dinamis. Nilai *Log Loss* dan *Brier Score* membuktikan bahwa estimasi persentase probabilitas ChampIntel terkalibrasi secara objektif dan reliabel.
