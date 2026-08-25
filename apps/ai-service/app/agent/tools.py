import os
import json
from app.services.predictor import predictor

def tool_predict_match(match_data: dict) -> dict:
    """
    Tool 1: Menghitung probabilitas kemenangan, seri, dan peluang lolos via model XGBoost.
    """
    res = predictor.predict_raw(match_data)
    return {
        "tool_name": "tool_predict_match",
        "status": "success",
        "data": {
            "home_win_prob": res["home_win_prob"],
            "draw_prob": res["draw_prob"],
            "away_win_prob": res["away_win_prob"],
            "home_qualification_prob": res.get("home_qualification_prob"),
            "away_qualification_prob": res.get("away_qualification_prob")
        }
    }


def tool_explain_shap(match_data: dict) -> dict:
    """
    Tool 2: Mengekstrak faktor kontribusi fitur matematis (SHAP Values).
    """
    res = predictor.predict_raw(match_data)
    return {
        "tool_name": "tool_explain_shap",
        "status": "success",
        "data": {
            "top_factors": res.get("top_factors", []),
            "primary_factor": res["top_factors"][0]["feature"] if res.get("top_factors") else "Keseimbangan ELO"
        }
    }


def tool_query_team_intelligence(team_name: str) -> dict:
    """
    Tool 3: Menarik profil statistik dan rating True Elo tim dari database lokal.
    """
    stats = predictor.team_stats.get(
        team_name,
        {"elo_rating": 1500.0, "avg_scored": 1.4, "avg_conceded": 1.2, "total_matches": 0}
    )
    return {
        "tool_name": "tool_query_team_intelligence",
        "status": "success",
        "data": {
            "team": team_name,
            "elo_rating": stats.get("elo_rating", 1500.0),
            "avg_scored": stats.get("avg_scored", 1.4),
            "avg_conceded": stats.get("avg_conceded", 1.2),
            "total_matches": stats.get("total_matches", 0)
        }
    }


def tool_simulate_scenario(match_data: dict, scenario_type: str) -> dict:
    """
    Tool 4: Mengeksekusi simulasi taktik what-if (All-Out Attack, Neutral Venue, dll).
    """
    sim = predictor.simulate_scenario(match_data, scenario_type)
    return {
        "tool_name": "tool_simulate_scenario",
        "status": "success",
        "data": sim
    }


def tool_model_confidence_metrics() -> dict:
    """
    Tool 5: Memberikan transparansi metrik ilmiah (Log Loss, Brier Score, Akurasi) 
    untuk menjawab pertanyaan user terkait keyakinan data/reliabilitas sistem.
    """
    return {
        "tool_name": "tool_model_confidence_metrics",
        "status": "success",
        "data": {
            "training_samples": 25979,
            "test_samples": 5196,
            "accuracy": "50.33%",
            "log_loss": 0.9963,
            "brier_score": 0.5950,
            "validation_method": "Temporal Split (Anti Data-Leakage)",
            "calibration_status": "Well-Calibrated (Brier < 0.60)"
        }
    }


# Kamus Registry Tool OpenClaw
TOOL_REGISTRY = {
    "predict_match": tool_predict_match,
    "explain_shap": tool_explain_shap,
    "team_intelligence": tool_query_team_intelligence,
    "simulate_scenario": tool_simulate_scenario,
    "model_confidence": tool_model_confidence_metrics
}