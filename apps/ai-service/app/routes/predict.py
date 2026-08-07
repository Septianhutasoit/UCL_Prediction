from fastapi import APIRouter 
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.predictor import predictor

router = APIRouter(tags=["Prediction"])

@router.post("/predict", response_model=PredictionResponse)
async def predict_match(req: PredictionRequest):
    data_dict = req.model_dump()
    result = predictor.predict(data_dict)
    return PredictionResponse(**result)