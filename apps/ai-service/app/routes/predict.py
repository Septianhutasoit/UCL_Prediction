from fastapi import APIRouter 
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.predictor import predictor

router = APIRouter(tags=["Prediction"])

@router.post("/predict", response_model=PredictionResponse)
async def predict_match(req: PredictionRequest):
    data_dict = req.model_dump()
    result = predictor.predict(data_dict)
    return PredictionResponse(**result)

@router.post("/simulate")
async def simulate_match(req: PredictionRequest, scenario_type: str ="neutral_venue"):
    data_dict = req.model_dump()
    result = predictor.simulate_scenario(data_dict, scenario)
    return result