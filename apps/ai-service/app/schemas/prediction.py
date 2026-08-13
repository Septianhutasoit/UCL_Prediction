from pydantic import BaseModel
from typing import Optional

class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    match_leg: int
    home_leg1_score: Optional[int] = None
    away_leg1_score: Optional[int] = None

class PredictionResponse(BaseModel):
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    home_qualification_prob: Optional[float] = None
    away_qualification_prob: Optional[float] = None
    ai_analysis: str