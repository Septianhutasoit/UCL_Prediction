import os
import re
import random
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
# dipakai untuk membedakan "general_analysis" (masih relevan) dari "out_of_scope".
GENERAL_FOOTBALL_KEYWORDS = [
    "menang", "kalah", "seri", "peluang", "prediksi", "prediction", "skor", "score",
    "gol", "goal", "laga", "pertandingan", "match", "main", "bermain", "play",
    "bola", "tim", "team", "klub", "club", "leg", "analisis", "analysis",
    "taktik", "tactic", "win", "lose", "draw", "chance", "probability",
    "game", "babak", "agregat", "aggregate", "juara", "final", "liga",
]


class ChampIntelAgent:
    def __init__(self):
        print(">>> 🤖 ChampIntel Hybrid Agent (2-Stage: Ground Truth Engine + NL Synthesizer) AKTIF! <<<")
        self.tools = TOOL_REGISTRY

    def _classify_semantic_intent(self, query: str, home: str, away: str, chat_history: list = None) -> tuple[str, bool]:
        """
        NLU semantik: deteksi maksud dari sinonim, dwibahasa ID/EN, riwayat chat, atau tandai out-of-scope.
        Return (intent, is_contextual_fallback) — is_contextual_fallback True HANYA JIKA intent
        diambil dari riwayat chat (anaphora resolution), bukan dari pertanyaan saat ini secara langsung.
        """
        q_lower = query.lower()

        # 1. Direct match pada query saat ini — topik mandiri baru, BUKAN konteks lanjutan
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, q_lower):
                    return intent, False

        # 2. Anaphora resolution: query pendek/ambigu ("lalu?", "bagaimana caranya?")
        #    -> cari topik dari pertanyaan user sebelumnya di riwayat chat
        if chat_history:
            for msg in reversed(chat_history):
                if msg.get("role") == "user":
                    last_q = msg.get("content", "").lower()
                    for intent, patterns in INTENT_PATTERNS.items():
                        for pattern in patterns:
                            if re.search(pattern, last_q):
                                return intent, True
                    break

        # 3. Masih relevan sepak bola/laga ini? (pertanyaan baru yang berdiri sendiri)
        mentions_team = home.lower() in q_lower or away.lower() in q_lower
        mentions_football = any(kw in q_lower for kw in GENERAL_FOOTBALL_KEYWORDS)
        if mentions_team or mentions_football:
            return "general_analysis", False

        return "out_of_scope", False

    # 🔬 TAHAP 1: DETERMINISTIC GROUND TRUTH ENGINE (Mengumpulkan Fakta Keras)
    
    def _gather_ground_truth(self, match_data: dict, home: str, away: str, intent: str) -> tuple[dict, list]:
        """
        Tahap 1: Data deterministik murni dari XGBoost, SHAP, True Elo, dan DB.
        Bentuk dict ini WAJIB cocok dengan yang dibaca llm_service.synthesize_response().
        """
        cached_res = predictor.predict_raw(match_data)
        tools_called = ["Tool: XGBoost Predictor", "Tool: SHAP Engine"]

        pred_data = self.tools["predict_match"](match_data, cached_res)["data"]
        shap_data = self.tools["explain_shap"](match_data, cached_res)["data"]

        h_info = self.tools["team_intelligence"](home)["data"]
        a_info = self.tools["team_intelligence"](away)["data"]
        tools_called.append("Tool: Team Intelligence DB")

        h_elo = h_info.get("elo_rating", 1500.0)
        a_elo = a_info.get("elo_rating", 1500.0)

        # Fallback ganda (_5 dulu, baru non-_5) — diselesaikan DI SINI (Tahap 1),
        # supaya llm_service.py cukup baca dict "form" yang sudah bersih.
        form = {
            "home_scored": h_info.get("avg_scored_5", h_info.get("avg_scored", 1.4)),
            "home_conceded": h_info.get("avg_conceded_5", h_info.get("avg_conceded", 1.2)),
            "away_scored": a_info.get("avg_scored_5", a_info.get("avg_scored", 1.2)),
            "away_conceded": a_info.get("avg_conceded_5", a_info.get("avg_conceded", 1.3)),
            "home_points_5": h_info.get("form_pts_5", h_info.get("form_pts", 7)),
            "away_points_5": a_info.get("form_pts_5", a_info.get("form_pts", 6)),
        }

        conf_data = None
        if intent == "model_validation":
            conf_data = self.tools["model_confidence"]()["data"]
            tools_called.append("Tool: Model Scientific Validation")

        scenario_data = None
        if intent == "scenario_simulation":
            q_lower = (match_data.get("current_query") or "").lower()
            scenario_type = "neutral_venue" if ("netral" in q_lower or "neutral" in q_lower) else "aggressive_tactic"
            scenario_data = self.tools["simulate_scenario"](match_data, scenario_type)["data"]
            tools_called.append("Tool: What-if Simulator")

        ground_truth = {
            "match_info": {
                "home_team": home,
                "away_team": away,
                "match_leg": match_data.get("match_leg", 1),
            },
            "probabilities": {
                "home_win_prob": pred_data["home_win_prob"],
                "draw_prob": pred_data["draw_prob"],
                "away_win_prob": pred_data["away_win_prob"],
            },
            "primary_factor": shap_data["primary_factor"],
            "elo": {"home": h_elo, "away": a_elo, "difference": round(h_elo - a_elo, 1)},
            "form": form,
            "scientific_metrics": conf_data,
            "scenario": scenario_data,
        }
        return ground_truth, tools_called

    # 🚀 ORCHESTRATOR UTAMA (Menghubungkan Tahap 1 & Tahap 2)
    def run(self, user_query: str, match_data: dict, chat_history: list = None) -> dict:
        home = match_data.get("home_team", "Home Team")
        away = match_data.get("away_team", "Away Team")
        leg = match_data.get("match_leg", 1)
        h_score = match_data.get("home_leg1_score", 0)
        a_score = match_data.get("away_leg1_score", 0)

        # Klasifikasi intent SEKALI di sini — kalau di luar konteks, berhenti total
        # tanpa menjalankan Tahap 1 (XGBoost/SHAP) atau Tahap 2 (LLM) sama sekali.
        intent, is_contextual_fallback = self._classify_semantic_intent(user_query, home, away, chat_history)

        if intent == "out_of_scope":
            decline_variations = [
                (
                    f"Maaf, itu di luar cakupan saya. Saya cuma bisa bantu analisis pertandingan UEFA Champions League "
                    f"berdasarkan data statistik & model prediksi — misalnya soal peluang menang, kelemahan tim, "
                    f"simulasi taktik, atau duel kunci antara {home} dan {away}."
                ),
                (
                    f"Saya tidak punya data untuk menjawab itu — fokus saya cuma seputar analisis taktik dan statistik laga "
                    f"{home} vs {away} (Elo, performa gol, form, dan simulasi skenario). Coba tanyakan hal seputar itu ya."
                ),
            ]
            return {
                "response": random.choice(decline_variations),
                "intent": intent,
                "tools_called": [],
                "ground_truth": None,
            }

        # Tahap 1: kumpulkan fakta keras (deterministik, tidak menyusun kalimat)
        match_data_with_query = {**match_data, "current_query": user_query}
        gt, tools_called = self._gather_ground_truth(match_data_with_query, home, away, intent)

        # Tahap 2: sintesis narasi — delegasikan ke llm_service (generatif kalau
        # Qwen aktif, fallback kaya-variasi kalau tidak). agent.py TIDAK menyusun
        # kalimat sendiri lagi di sini.
        response_text = llm_service.synthesize_response(user_query, intent, gt, chat_history)

        # Penanda konteks multi-turn — HANYA muncul kalau intent-nya benar-benar
        # diambil dari riwayat chat (anaphora resolution), bukan sekadar karena
        # ada riwayat. Pertanyaan baru yang mandiri tetap bersih tanpa tag ini.
        if is_contextual_fallback:
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
                "home_win_prob": gt["probabilities"]["home_win_prob"],
                "away_win_prob": gt["probabilities"]["away_win_prob"],
                "draw_prob": gt["probabilities"]["draw_prob"],
                "top_factor": gt["primary_factor"],
            },
        }


agent = ChampIntelAgent()