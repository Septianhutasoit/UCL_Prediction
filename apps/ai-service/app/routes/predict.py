from fastapi import APIRouter
from app.schemas.prediction import PredictionRequest, PredictionResponse

router = APIRouter(tags=["Prediction"])

@router.post("/predict", response_model=PredictionResponse)
async def predict_match(req: PredictionRequest):
    # --- MOCK LOGIC (Nanti diganti XGBoost + SHAP + Qwen asli) ---
    
    analysis = f"Analisis AI (Mock): Pertandingan Leg {req.match_leg} antara {req.home_team} dan {req.away_team} berjalan ketat berdasarkan data statistik."
    
    # Jika Leg 2, sertakan peluang kelolosan
    if req.match_leg == 2:
        analysis += " Karena ini Leg 2, agregat dari leg sebelumnya sangat memengaruhi peluang lolos."
        return PredictionResponse(
            home_win_prob=0.48,
            draw_prob=0.27,
            away_win_prob=0.25,
            home_qualification_prob=0.55,
            away_qualification_prob=0.45,
            ai_analysis=analysis
        )
    else:
        # Jika Leg 1
        return PredictionResponse(
            home_win_prob=0.52,
            draw_prob=0.25,
            away_win_prob=0.23,
            ai_analysis=analysis
        )