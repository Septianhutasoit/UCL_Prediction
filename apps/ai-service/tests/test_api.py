from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200


def test_predict_real_madrid_vs_bayern():
    """Uji Prediksi Laga: Real Madrid vs Bayern Munich"""
    payload = {
        "home_team": "Real Madrid",
        "away_team": "Bayern Munich",
        "match_leg": 1,
        "home_leg1_score": 0,
        "away_leg1_score": 0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "home_win_prob" in data
    assert len(data["top_factors"]) > 0


def test_predict_arsenal_vs_psg_leg2():
    """Uji Prediksi Leg 2 dengan agregat: Arsenal vs PSG"""
    payload = {
        "home_team": "Arsenal",
        "away_team": "Paris Saint-Germain",
        "match_leg": 2,
        "home_leg1_score": 1,
        "away_leg1_score": 0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["home_qualification_prob"] is not None


def test_simulate_scenario_endpoint():
    payload = {
        "home_team": "Barcelona",
        "away_team": "Borussia Dortmund",
        "match_leg": 1,
    }
    response = client.post("/simulate?scenario=aggressive_tactic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scenario_name" in data


def test_agent_manchester_city_vs_inter():
    """Uji dinamika agen untuk kombinasi tim berbeda: Man City vs Inter"""
    payload = {
        "home_team": "Manchester City",
        "away_team": "Inter",
        "match_leg": 1,
        "current_query": "Apa kelemahan utama Inter?",
    }
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "defensive_weakness"
    assert "Inter" in data["response"]
    assert "Manchester City" in data["response"]


def test_agent_juventus_vs_aston_villa_elo_inquiry():
    """Uji dinamika agen untuk kombinasi tim berbeda: Juventus vs Aston Villa"""
    payload = {
        "home_team": "Juventus",
        "away_team": "Aston Villa",
        "match_leg": 1,
        "current_query": "darimana data keyakinan ini?",
    }
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "model_validation"
    assert "Juventus" in data["response"]
    assert "Aston Villa" in data["response"]


def test_agent_english_query():
    """Uji NLU semantik dalam bahasa Inggris: key matchup"""
    payload = {
        "home_team": "Liverpool",
        "away_team": "Bayer Leverkusen",
        "match_leg": 1,
        "current_query": "What is the key midfield matchup?",
    }
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "key_matchup"
    assert "Liverpool" in data["response"]


def test_agent_english_nlu_defensive_weakness():
    """Uji NLU semantik dalam bahasa Inggris: defensive weakness"""
    payload = {
        "home_team": "Real Madrid",
        "away_team": "Bayern Munich",
        "match_leg": 1,
        "current_query": "What is the main defensive weakness of the away team?",
    }
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "defensive_weakness"
    assert "Tool: Team Intelligence DB" in data["tools_called"]


def test_agent_multiturn_memory():
    """
    Uji memori multi-turn: agen mengingat konteks pertanyaan sebelumnya
    lewat chat_history, dan menandai responsnya dengan '[Konteks Lanjutan]'.
    PENTING: jangan hapus test ini — ini yang memverifikasi fitur multi-turn
    tetap berfungsi setiap kali agent.py diubah.
    """
    payload = {
        "home_team": "Real Madrid",
        "away_team": "Bayern Munich",
        "match_leg": 1,
        "current_query": "Lalu bagaimana cara mengeksploitasinya?",
        "chat_history": [
            {"role": "user", "content": "Apa kelemahan Bayern Munich?"},
            {"role": "assistant", "content": "Kelemahan Bayern ada pada rest-defense..."},
        ],
    }
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "defensive_weakness"
    assert "[Konteks Lanjutan]" in data["response"]