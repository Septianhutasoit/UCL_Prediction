from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Lis, Dict, Any
from app.agent.agent import agent

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class AgentQueryRequest(BaseModel):
    home_team: str
    away_team: str
    match_leg: int = 1
    home_leg1_score: Optional[int] = 0
    away_leg1_score: Optional[int] = 0
    current_query: str
    chat_history: Optional[List[ChatMessage]] = []


@router.post("/query")
def query_agent(req: AgentQueryRequest):
    # Data pertandingan yang akan disuntikkan ke otak agent
    match_data = {
        "home_team": req.home_team,
        "away_team": req.away_team,
        "match_leg": req.match_leg,
        "home_leg1_score": req.home_leg1_score or 0,
        "away_leg1_score": req.away_leg1_score or 0,  # <-- BUG away_leg1_score DIPERBAIKI
    }

    # Format riwayat chat menjadi list of dict sederhana
    history = [{"role": m.role, "content": m.content} for m in req.chat_history] if req.chat_history else []

    # Jalankan penalar taktis AI Agent
    result = agent.run(
        user_query=req.current_query,
        match_data=match_data,
        chat_history=history
    )

    return result