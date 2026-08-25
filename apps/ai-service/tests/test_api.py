from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_predict_endpoint():
    """Uji apakah model XGBoost mengembalikan probabilitas valid dan faktor SHAP"""
    payload = {
        "home_team": "Real Madrid",
        "away_team": "Bayern Munich",
        "match_leg": 1,
        "home_leg1_score": 0,
        "away_leg1_score": 0
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Validasi output probabilitas & SHAP
    assert "home_win_prob" in data
    assert "draw_prob" in data
    assert "away_win_prob" in data
    assert "top_factors" in data
    assert len(data["top_factors"]) > 0

    # Total probabilitas harus 100% (1.0)
    total_prob = data["home_win_prob"] + data["draw_prob"] + data["away_win_prob"]
    assert 0.98 <= total_prob <= 1.02


def test_simulate_scenario_endpoint():
    """Uji apakah simulator what-if merespons perubahan taktik"""
    payload = {
        "home_team": "Real Madrid",
        "away_team": "Bayern Munich",
        "match_leg": 1
    }
    response = client.post("/simulate?scenario=aggressive_tactic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scenario_name" in data
    assert "probability_difference" in data


def test_agent_query_endpoint():
    """Uji apakah Autonomous Agent memanggil tool dan mengembalikan respons"""
    payload = {
        "home_team": "Real Madrid",
        "away_team": "Bayern Munich",
        "match_leg": 1,
        "current_query": "Apakah kamu yakin dengan data ini?"
    }
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "tools_called" in data
    assert "intent" in data
    assert len(data["tools_called"]) > 0