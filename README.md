<div align="center">
  
  <!-- UCL THEMED HEADER -->
  <img src="https://readme-typing-svg.demolab.com?font=Plus+Jakarta+Sans&weight=800&size=44&duration=3000&pause=500&color=0F4C81&center=true&vCenter=true&random=false&width=600&height=80&lines=🏆+UCL+MADRID;ChampIntel+AI+Masterplan" alt="UCL Madrid Header" />
  
  <p align="center">
    <strong>⚽ UEFA Champions League — Real Madrid AI Predictor & Analytics Engine</strong>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/UCL_2025/26-Real_Madrid-0F4C81?style=for-the-badge&logo=uefa&logoColor=white" />
    <img src="https://img.shields.io/badge/Architecture-Monorepo-007ACC?style=for-the-badge" />
    <img src="https://img.shields.io/badge/Backend-Go_Gin-00ADD8?style=for-the-badge&logo=go&logoColor=white" />
    <img src="https://img.shields.io/badge/AI-FastAPI_%2B_XGBoost_%2B_Qwen-FF69B4?style=for-the-badge&logo=python&logoColor=white" />
  </p>

</div>

---

## 🖼️ UCL Madrid — Banner & Preview

<div align="center">

  <!-- IMAGE BANNER -->
  <img src="./apps/web/public/UCL.jpg" alt="UCL Real Madrid" width="100%" style="border-radius: 16px; max-width: 900px; box-shadow: 0 20px 60px rgba(0,0,0,0.5);" />

  <p align="center" style="margin-top: 0.75rem; color: rgba(255,255,255,0.5); font-size: 0.85rem;">
    ⚽ Real Madrid UCL Analytics • 2025/26 Season
  </p>

</div>

---

## 📖 About This Media

| Detail | Informasi |
|--------|-----------|
| 🏆 **Event** | UEFA Champions League 2025/26 |
| ⚪ **Team** | Real Madrid C.F. |
| 🖼️ **Format** | Banner Image (JPG) |
| 📁 **Path** | `./apps/web/public/UCL.jpg` |

---

## 🚀 ChampIntel AI — Masterplan Proyek

Sistem analisis dan pemodelan prediktif UEFA Champions League berbasis microservice, menggabungkan pemrosesan data statistik XGBoost dan narasi analisis LLM Qwen (QLoRA).

### 🏗️ Arsitektur Monorepo
* **`apps/api` (Go + Gin):** Service core backend & API Gateway berkinerja tinggi untuk menangani request client.
* **`apps/ai-service` (Python + FastAPI):** Service inference machine learning (XGBoost, SHAP, Qwen LLM).
* **`apps/web` (Next.js / React):** Web dashboard & UI platform visualisasi statistik.
* **`ml/`:** Pipeline training, pengolahan dataset, serta notebook eksperimen model.
* **`infra/`:** Konfigurasi Docker, Docker Compose, dan deployment.

---

### 📊 Machine Learning Pipeline (XGBoost + SHAP)
* **18 Fitur Terarah:** Mengelompokkan tren performa, formasi, efisiensi gol, dan statistik laga.
* **Dinamika Leg 1 & Leg 2:** Penanganan fase gugur menggunakan akumulasi fitur `aggregate_difference` dan `home/away_aggregate_before`.
* **Explainable AI (XAI):** Penggunaan **SHAP** untuk transparansi kontribusi setiap fitur terhadap probabilitas kemenangan.

---

### 🤖 LLM Reasoning Engine (Qwen + QLoRA)
* **Anti-Hallucination Guardrails:** System prompt terstruktur dengan dataset ramping (100–200 sampel terverifikasi) agar narasi LLM konsisten terhadap data XGBoost & SHAP.
* **Fine-Tuning:** Memakai metode **QLoRA** untuk efisiensi resource GPU tanpa mengorbankan kualitas analisis teknis.

---

### 📈 Metrik Evaluasi Model
* **Probabilitas Pertandingan:** Evaluasi performa model menggunakan **Log Loss** dan **Brier Score**.
* **Kualitas Narasi AI:** Evaluasi keluaran teks LLM menggunakan metrik **Faithfulness** terhadap output statistik.