from app.services.predictor import predictor

def tool_get_match_stats(home_team: str, away_team: str):
    """Tool untuk mengambil statistik dasar klub."""
    h_stats = predictor.team_stats.get(home_team, {"avg_scored": 1.5, "avg_conceded": 1.0, "win_rate": 0.5})
    a_stats = predictor.team_stats.get(away_team, {"avg_scored": 1.3, "avg_conceded": 1.2, "win_rate": 0.4})
    return {
        "home_team": home_team, "home_stats": h_stats,
        "away_team": away_team, "away_stats": a_stats
    }

def tool_predict_match(home_team: str, away_team: str, match_leg: int, home_leg1: int = 0, away_leg1: int = 0):
    """Tool utama untuk menjalankan prediksi XGBoost & analisis agregat."""
    payload = {
        "home_team": home_team,
        "away_team": away_team,
        "match_leg": match_leg,
        "home_leg1_score": home_leg1,
        "away_leg1_score": away_leg1,
        "elo_difference": 0.0
    }
    return predictor.predict(payload)

def tool_simulate_what_if(home_team: str, away_team: str, scenario: str):
    """Tool untuk simulasi What-if Scenario."""
    payload = {
        "home_team": home_team,
        "away_team": away_team,
        "match_leg": 2,
        "home_leg1_score": 1,
        "away_leg1_score": 1,
        "elo_difference": 0.0
    }
    return predictor.simulate_scenario(payload, scenario)