 # 🏛️ ChampIntel System Architecture

ChampIntel menggunakan arsitektur **Microservices Monorepo** yang terbagi menjadi 3 lapisan utama:
1. **Frontend Layer (Next.js 14):** Antarmuka pengguna interaktif, simulator what-if, dan chatbot taktis.
2. **Gateway Layer (Go + Gin):** Router API berkecepatan tinggi dengan latensi rendah (< 20 ms) dan proteksi CORS.
3. **AI & Agent Layer (FastAPI + OpenClaw):** Engine kalkulasi probabilitas XGBoost, SHAP Explainability, dan Qwen 2.5 Agent.
