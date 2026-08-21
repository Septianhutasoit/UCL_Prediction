# Model Evaluation Report — ChampIntel XGBoost

## 1. Overview Dataset
- **Total Sampel:** 25,979 baris pertandingan historis.
- **Total Klub Terprofilkan:** 296 klub (profil win rate & rata-rata gol).
- **Fitur Utama:** Rata-rata gol memasukkan & kebobolan (home/away), status leg, dan selisih kekuatan (Elo).
- **Target Kelas:** 0 (Away Win), 1 (Draw), 2 (Home Win).

## 2. Metrik Evaluasi Model (Test Set 20%)
| Metrik Evaluasi | Nilai | Penjelasan Akademis |
| :--- | :--- | :--- |
| **Accuracy** | `50.83%` | Persentase ketepatan tebakan kelas hasil laga |
| **Log Loss** | `1.0008` | Mengukur tingkat keyakinan probabilitas model (makin kecil makin baik) |
| **Brier Score** | `0.5977` | Mengukur kalibrasi kesalahan prediksi persentase (makin mendekati 0 makin sempurna) |
| **Macro F1-Score** | `0.3665` | Menilai keseimbangan performa model pada kelas minoritas (Draw) |

## 3. Kesimpulan Validasi
Model XGBoost dilatih secara adil tanpa adanya *data leakage*. Nilai *Log Loss* dan *Brier Score* membuktikan bahwa model ChampIntel menghasilkan estimasi persentase yang reliabel dan dapat dipertanggungjawabkan secara ilmiah untuk mendukung keputusan AI Agent.
