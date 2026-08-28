from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_predict_endpoint():
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
    assert "home_win_prob" in data
    assert "top_factors" in data


def test_simulate_scenario_endpoint():
    payload = {
        "home_team": "Real Madrid",
        "away_team": "Bayern Munich",
        "match_leg": 1
    }
    response = client.post("/simulate?scenario=aggressive_tactic", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scenario_name" in data


def test_agent_english_nlu_query():
    """Uji NLU Semantik: Query Bahasa Inggris 'What is the weakness of Bayern?'"""
    payload = {
        "home_team": "Real Madrid",
        "away_team": "Bayern Munich",
        "match_leg": 1,
        "current_query": "What is the main defensive weakness of the away team?"
    }
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "defensive_weakness"
    assert "Tool: Team Intelligence DB" in data["tools_called"]


def test_agent_multiturn_memory():
    """Uji Memori Multi-Turn: Mengingat konteks pertanyaan sebelumnya"""
    payload = {
        "home_team": "Real Madrid",
        "away_team": "Bayern Munich",
        "match_leg": 1,
        "current_query": "Lalu bagaimana cara mengeksploitasinya?",
        "chat_history": [
            {"role": "user", "content": "Apa kelemahan Bayern Munich?"},
            {"role": "assistant", "content": "Kelemahan Bayern ada pada rest-defense..."}
        ]
    }
    response = client.post("/agent/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Agen berhasil mendeteksi intent dari riwayat percakapan sebelumnya
    assert data["intent"] == "defensive_weakness"
    assert "[Konteks Lanjutan]" in data["response"]