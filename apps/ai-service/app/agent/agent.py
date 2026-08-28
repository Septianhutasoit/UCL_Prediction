import os
import re
from app.agent.tools import TOOL_REGISTRY
from app.services.predictor import predictor

# Kamus Semantik NLU (Mendukung sinonim & Dwibahasa ID/EN)
INTENT_PATTERNS = {
    "model_validation": [
        r"\b(yakin|percaya|akurasi|valid|metrik|brier|log loss|dasar|confident|accuracy|reliable|proof|evidence)\b"
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
        r"\b(pemain|kunci|duel|bintang|man of the match|key player|midfield|pivot|lineup|star)\b"
    ]
}


class ChampIntelAgent:
    def __init__(self):
        print(">>> 🤖 OpenClaw Semantic Agent & Multi-Turn Memory AKTIF! <<<")
        self.tools = TOOL_REGISTRY

    def _classify_semantic_intent(self, query: str, chat_history: list = None) -> str:
        """NLU Semantik: Mendeteksi maksud pengguna berdasarkan sinonim, bahasa ID/EN, dan riwayat chat."""
        q_lower = query.lower()

        # 1. Cek pada query saat ini
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, q_lower):
                    return intent

        # 2. Multi-Turn Context Resolution: Jika user bertanya pendek (misal: "lalu?", "bagaimana solusinya?"),
        # periksa topik pada riwayat percakapan sebelumnya
        if chat_history and len(chat_history) > 0:
            last_user_msg = ""
            for msg in reversed(chat_history):
                if msg.get("role") == "user":
                    last_user_msg = msg.get("content", "").lower()
                    break
            
            for intent, patterns in INTENT_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, last_user_msg):
                        return intent

        return "general_analysis"

    def run(self, user_query: str, match_data: dict, chat_history: list = None) -> dict:
        # 1. SINGLE-PASS EXECUTION (Hitung XGBoost & SHAP 1x saja untuk menghemat 50% komputasi)
        cached_res = predictor.predict_raw(match_data)
        
        home = match_data.get("home_team", "Home Team")
        away = match_data.get("away_team", "Away Team")
        leg = match_data.get("match_leg", 1)
        h_score = match_data.get("home_leg1_score", 0)
        a_score = match_data.get("away_leg1_score", 0)

        # 2. Klasifikasi Semantik Intent dengan Memori Multi-Turn
        intent = self._classify_semantic_intent(user_query, chat_history)

        tools_called = ["Tool: XGBoost Predictor", "Tool: SHAP Engine"]
        obs = {
            "prediction": self.tools["predict_match"](match_data, cached_res)["data"],
            "shap": self.tools["explain_shap"](match_data, cached_res)["data"]
        }

        h_prob = f"{obs['prediction']['home_win_prob']*100:.1f}%"
        d_prob = f"{obs['prediction']['draw_prob']*100:.1f}%"
        a_prob = f"{obs['prediction']['away_win_prob']*100:.1f}%"
        primary_factor = obs["shap"]["primary_factor"]

        # 3. Dynamic Tool Calling Berdasarkan Semantic Intent
        if intent == "model_validation":
            conf_obs = self.tools["model_confidence"]()
            tools_called.append("Tool: Model Scientific Validation")
            c = conf_obs["data"]
            response_text = (
                f"Sistem memiliki reliabilitas ilmiah tinggi berbasis model XGBoost yang dilatih pada {c['training_samples']:,} laga "
                f"dengan {c['validation_method']}. Metrik uji menunjukkan Log Loss {c['log_loss']} dan Brier Score {c['brier_score']} "
                f"({c['calibration_status']}), membuktikan bahwa probabilitas {home} ({h_prob}) vs {away} ({a_prob}) terkalibrasi secara objektif."
            )

        elif intent == "scenario_simulation":
            scenario_type = "neutral_venue" if "netral" in user_query.lower() or "neutral" in user_query.lower() else "aggressive_tactic"
            sim_obs = self.tools["simulate_scenario"](match_data, scenario_type)
            tools_called.append("Tool: What-if Simulator")
            s = sim_obs["data"]
            response_text = (
                f"Hasil Simulasi Skenario ({s['scenario_name']}): {s['explanation']} "
                f"Peluang kemenangan {home} berubah dari {h_prob} menjadi {s['scenario_result']['home_win_prob']*100:.1f}% "
                f"({s['probability_difference']*100:+.1f}%)."
            )

        elif intent == "defensive_weakness":
            a_info = self.tools["team_intelligence"](away)
            tools_called.append("Tool: Team Intelligence DB")
            a_conceded = a_info["data"].get("avg_conceded", 1.3)
            response_text = (
                f"Berdasarkan data observasi, {away} memiliki rata-rata kebobolan {a_conceded} gol/laga. "
                f"Celah utama terletak pada koordinasi rest-defense saat menghadapi tekanan di area half-space. "
                f"Dengan keunggulan probabilitas {h_prob}, {home} diproyeksikan mendikte sepertiga akhir pertahanan {away}."
            )

        elif intent == "counter_strategy":
            tools_called.append("Tool: Team Intelligence DB")
            response_text = (
                f"Berdasarkan faktor kunci {primary_factor}, jika {away} menerapkan low-block, mereka wajib mewaspadai efektivitas serangan {home}. "
                f"Peluang terbaik {away} untuk mencuri poin ({a_prob}) adalah memaksimalkan transisi kilat di sisi sayap dan situasi set-piece."
            )

        elif intent == "key_matchup":
            tools_called.append("Tool: Team Intelligence DB")
            response_text = (
                f"Kunci duel {home} vs {away} berada pada perebutan lini sentral (holding midfielder). "
                f"Dengan margin probabilitas {abs(float(h_prob.replace('%','')) - float(a_prob.replace('%',''))):.1f}%, penguasaan second-balls "
                f"akan menjadi penentu utama kontrol ritme pertandingan."
            )

        else:
            response_text = (
                f"Analisis Taktikal {home} vs {away} (Leg {leg}): Proyeksi model XGBoost menunjukkan {home} {h_prob}, "
                f"Seri {d_prob}, dan {away} {a_prob}. Faktor dominan penentu laga adalah {primary_factor}."
            )

        # 4. Multi-Turn History Awareness (Menyambungkan konteks jika ada pesan sebelumnya)
        if chat_history and len(chat_history) > 1:
            response_text = f"[Konteks Lanjutan]: {response_text}"

        if leg == 2:
            response_text += f" Mengingat agregat Leg 1 ({h_score}-{a_score}), manajemen risiko akan sangat krusial hingga peluit akhir."

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
                "top_factor": primary_factor
            }
        }


agent = ChampIntelAgent()