import os
import re
from app.agent.tools import TOOL_REGISTRY
from app.services.predictor import predictor
from app.services.llm_service import llm_service

# Kamus Semantik NLU (mendukung sinonim & dwibahasa ID/EN)
INTENT_PATTERNS = {
    "model_validation": [
        r"\b(yakin|percaya|akurasi|valid|metrik|brier|log loss|dasar|confident|accuracy|reliable|proof|evidence|darimana|dari mana|sumber|dataset|data ini|historis)\b"
    ],
    "scenario_simulation": [
        r"\b(skenario|agresif|all out|what if|netral|simulasi|scenario|aggressive|neutral venue|simulate)\b"
    ],
    "defensive_weakness": [
        r"\b(lemah|kelemahan|celah|kebobolan|titik lemah|kekurangan|weakness|vulnerability|flaw|concede|leak)\b"
    ],
    "counter_strategy": [
        r"\b(taktik|bertahan|parkir bus|counter|serangan balik|strategi|tactics|defend|low block|counter attack|strategy)\b"
    ],
    "key_matchup": [
        r"\b(pemain|kunci|duel|bintang|man of the match|key player|midfield|pivot|lineup|star|gelandang)\b"
    ],
}

# Kata kunci umum yang menandakan pertanyaan MASIH seputar sepak bola/laga,
# meski tidak cocok dengan pola intent spesifik di atas — dipakai untuk
# membedakan "general_analysis" (masih relevan) dari "out_of_scope" (tidak relevan sama sekali).
GENERAL_FOOTBALL_KEYWORDS = [
    "menang", "kalah", "seri", "peluang", "prediksi", "prediction", "skor", "score",
    "gol", "goal", "laga", "pertandingan", "match", "main", "bermain", "play",
    "bola", "tim", "team", "klub", "club", "leg", "analisis", "analysis",
    "taktik", "tactic", "win", "lose", "draw", "chance", "probability",
    "game", "babak", "agregat", "aggregate", "juara", "final", "liga",
]


class ChampIntelAgent:
    def __init__(self):
        print(">>> 🤖 ChampIntel Hybrid Agent (Deterministic Engine + LLM Synthesizer) AKTIF! <<<")
        self.tools = TOOL_REGISTRY

    def _classify_semantic_intent(self, query: str, home: str, away: str, chat_history: list = None) -> str:
        """NLU semantik: deteksi maksud dari sinonim, dwibahasa ID/EN, riwayat chat, atau tandai out-of-scope."""
        q_lower = query.lower()

        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, q_lower):
                    return intent

        # Multi-turn context resolution: query pendek/ambigu ("lalu?", "kenapa begitu?")
        # -> cek topik pertanyaan user sebelumnya di riwayat chat
        if chat_history:
            for msg in reversed(chat_history):
                if msg.get("role") == "user":
                    last_q = msg.get("content", "").lower()
                    for intent, patterns in INTENT_PATTERNS.items():
                        for pattern in patterns:
                            if re.search(pattern, last_q):
                                return intent
                    break

        # Masih relevan sepak bola/laga ini? (sebut nama tim, atau pakai kata kunci umum bola)
        mentions_team = home.lower() in q_lower or away.lower() in q_lower
        mentions_football = any(kw in q_lower for kw in GENERAL_FOOTBALL_KEYWORDS)

        if mentions_team or mentions_football:
            return "general_analysis"

        return "out_of_scope"

    def run(self, user_query: str, match_data: dict, chat_history: list = None) -> dict:
        home = match_data.get("home_team", "Home Team")
        away = match_data.get("away_team", "Away Team")
        leg = match_data.get("match_leg", 1)
        h_score = match_data.get("home_leg1_score", 0)
        a_score = match_data.get("away_leg1_score", 0)

        # 1. Klasifikasi intent DULU — kalau di luar konteks, langsung berhenti di sini
        #    tanpa buang komputasi XGBoost/SHAP untuk pertanyaan yang tidak relevan sama sekali.
        intent = self._classify_semantic_intent(user_query, home, away, chat_history)

        if intent == "out_of_scope":
            response_text = (
                f"Maaf, itu di luar cakupan saya. Saya cuma bisa bantu analisis pertandingan UEFA Champions League "
                f"berdasarkan data statistik & model prediksi — misalnya soal peluang menang, kelemahan tim, "
                f"simulasi taktik, atau duel kunci antara {home} dan {away}."
            )
            return {
                "response": response_text,
                "intent": intent,
                "tools_called": [],
                "ground_truth": None,
            }

        # 🔬 TAHAP 1: DETERMINISTIC ENGINE — Kumpulkan Fakta Keras (Ground Truth)
        cached_res = predictor.predict_raw(match_data)

        h_info = self.tools["team_intelligence"](home)["data"]
        a_info = self.tools["team_intelligence"](away)["data"]

        h_elo = h_info.get("elo_rating", 1500.0)
        a_elo = a_info.get("elo_rating", 1500.0)
        elo_diff = round(h_elo - a_elo, 1)

        h_sc = h_info.get("avg_scored_5", h_info.get("avg_scored", 1.4))
        h_cc = h_info.get("avg_conceded_5", h_info.get("avg_conceded", 1.2))
        a_sc = a_info.get("avg_scored_5", a_info.get("avg_scored", 1.2))
        a_cc = a_info.get("avg_conceded_5", a_info.get("avg_conceded", 1.3))
        h_pts = h_info.get("form_pts_5", h_info.get("form_pts", 7))
        a_pts = a_info.get("form_pts_5", a_info.get("form_pts", 6))

        tools_called = ["Tool: XGBoost Predictor", "Tool: SHAP Engine"]
        obs = {
            "prediction": self.tools["predict_match"](match_data, cached_res)["data"],
            "shap": self.tools["explain_shap"](match_data, cached_res)["data"],
        }

        h_prob_num = obs["prediction"]["home_win_prob"] * 100
        a_prob_num = obs["prediction"]["away_win_prob"] * 100
        d_prob_num = obs["prediction"]["draw_prob"] * 100

        h_prob = f"{h_prob_num:.1f}%"
        d_prob = f"{d_prob_num:.1f}%"
        a_prob = f"{a_prob_num:.1f}%"
        primary_factor = obs["shap"]["primary_factor"]

        q_lower = user_query.lower()

        # Paket fakta keras yang akan disuplai ke LLM (Tahap 2) — angka di sini
        # adalah SUMBER TUNGGAL kebenaran, LLM dilarang mengubahnya.
        ground_truth = {
            "match_info": {"home_team": home, "away_team": away, "match_leg": leg},
            "probabilities": {"home_win_prob": h_prob, "draw_prob": d_prob, "away_win_prob": a_prob},
            "primary_factor": primary_factor,
            "elo": {"home": h_elo, "away": a_elo, "difference": elo_diff},
            "form": {
                "home_scored": h_sc, "home_conceded": h_cc, "home_points_5": h_pts,
                "away_scored": a_sc, "away_conceded": a_cc, "away_points_5": a_pts,
            },
        }

        # Tarik data tool tambahan HANYA jika intent memerlukannya
        if intent == "model_validation":
            conf_obs = self.tools["model_confidence"]()
            tools_called.append("Tool: Model Scientific Validation")
            ground_truth["scientific_metrics"] = conf_obs["data"]

        elif intent == "scenario_simulation":
            scenario_type = "neutral_venue" if ("netral" in q_lower or "neutral" in q_lower) else "aggressive_tactic"
            sim_obs = self.tools["simulate_scenario"](match_data, scenario_type)
            tools_called.append("Tool: What-if Simulator")
            ground_truth["scenario"] = sim_obs["data"]

        elif intent in ("defensive_weakness", "counter_strategy", "key_matchup"):
            tools_called.append("Tool: Team Intelligence DB")

        # 🧠 TAHAP 2: LLM SYNTHESIZER — Susun Bahasa Alami dari Fakta di Atas
        response_text = llm_service.synthesize_response(
            user_query=user_query,
            intent=intent,
            ground_truth=ground_truth,
            chat_history=chat_history,
        )

        # Penanda konteks multi-turn — dipertahankan untuk verifikasi memori percakapan
        if chat_history and len(chat_history) > 1:
            response_text = f"[Konteks Lanjutan]: {response_text}"

        if leg == 2:
            response_text += (
                f" Membawa hasil agregat Leg 1 ({h_score}-{a_score}), manajemen risiko dan efektivitas "
                f"gol tandang akan sangat menentukan kelolosan."
            )

        return {
            "response": response_text,
            "intent": intent,
            "tools_called": tools_called,
            "ground_truth": {
                "home_team": home,
                "away_team": away,
                "home_win_prob": obs["prediction"]["home_win_prob"],
                "away_win_prob": obs["prediction"]["away_win_prob"],
                "draw_prob": obs["prediction"]["draw_prob"],
                "top_factor": primary_factor,
            },
        }


agent = ChampIntelAgent()