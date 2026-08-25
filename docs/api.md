 # 📡 ChampIntel API Documentation

Base URL: `http://localhost:8080/api/v1`

### Endpoints:
- `POST /predict`: Menghasilkan probabilitas hasil laga (Home Win, Draw, Away Win) dan faktor SHAP.
- `POST /simulate?scenario={type}`: Menjalankan simulasi taktik what-if (All-Out Attack, Neutral Venue).
- `POST /agent/query`: Endpoint percakapan multi-turn untuk Autonomous Tactical Agent.
