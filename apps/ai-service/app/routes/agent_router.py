from fastapi import APIRouter
from pydantic import BaseModel
from app.agent.agent import agent

router = APIRouter(tags=["AI Agent"])

class AgentQuery(BaseModel):
    query: str
    home_team: str
    away_team: str
    match_leg: int = 1
    home_leg1_score: int = 0
    away_leg1_score: int = 0

@router.post("/agent/query")
async def query_agent(req: AgentQuery):
    result = agent.run_agent(
        user_query=req.query,
        home_team=req.home_team,
        away_team=req.away_team,
        match_leg=req.match_leg,
        home_leg1_score=req.home_leg1_score,
        away_leg1_score=req.home_leg1_score
    )
    return result