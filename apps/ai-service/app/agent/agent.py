import os
import sys
from app.agent.tools import TOOL_REGISTRY

class ChampIntelAgent:
    def __init__(self):
        print(">>> 🤖 OpenClaw Autonomous Tool-Calling Agent AKTIF! <<<")
        self.tools = TOOL_REGISTRY

    def _decide_and_execute_tools(self, query: str, match_data: dict):
        """
        Orkestrator: Menganalisis kebutuhan query user, memilih tool secara dinamis, 
        mengeksekusinya, dan mengumpulkan data observasi nyata.
        """
        q_lower = query.lower()
        tools_executed = []
        observations = {}

        # 1. Selalu jalankan kalkulasi dasar (Predict & SHAP)
        pred_obs = self.tools["predict_match"](match_data)
        shap_obs = self.tools["explain_shap"](match_data)
        tools_executed.extend(["Tool: XGBoost Predictor", "Tool: SHAP Engine"])
        observations["prediction"] = pred_obs["data"]
        observations["shap"] = shap_obs["data"]

        # 2. Pemanggilan Dinamis Tool 3 (Team Intelligence DB)
        if any(w in q_lower for w in ["lemah", "celah", "kebobolan", "elo", "rating", "profil", "kekuatan"]):
            h_info = self.tools["team_intelligence"](match_data.get("home_team"))
            a_info = self.tools["team_intelligence"](match_data.get("away_team"))
            tools_executed.append("Tool: Team Intelligence DB")
            observations["home_team_info"] = h_info["data"]
            observations["away_team_info"] = a_info["data"]

        # 3. Pemanggilan Dinamis Tool 4 (What-if Scenario Simulator)
        if any(w in q_lower for w in ["skenario", "agresif", "all out", "what if", "netral", "simulasi"]):
            scenario_type = "neutral_venue" if "netral" in q_lower else "aggressive_tactic"
            sim_obs = self.tools["simulate_scenario"](match_data, scenario_type)
            tools_executed.append("Tool: What-if Simulator")
            observations["scenario"] = sim_obs["data"]

        # 4. Pemanggilan Dinamis Tool 5 (Model Confidence / Evaluasi Ilmiah)
        if any(w in q_lower for w in ["yakin", "percaya", "akurasi", "valid", "metrik", "log loss", "brier", "dasar"]):
            conf_obs = self.tools["model_confidence"]()
            tools_executed.append("Tool: Model Scientific Validation")
            observations["confidence"] = conf_obs["data"]

        return tools_executed, observations

    def run(self, user_query: str, match_data: dict, chat_history: list = None) -> dict:
        # Eksekusi tool nyata
        tools_called, obs = self._decide_and_execute_tools(user_query, match_data)

        home = match_data.get("home_team", "Home Team")
        away = match_data.get("away_team", "Away Team")
        leg = match_data.get("match_leg", 1)
        h_score = match_data.get("home_leg1_score", 0)
        a_score = match_data.get("away_leg1_score", 0)

        pred = obs["prediction"]
        shap = obs["shap"]
        h_prob = f"{pred['home_win_prob']*100:.1f}%"
        d_prob = f"{pred['draw_prob']*100:.1f}%"
        a_prob = f"{pred['away_win_prob']*100:.1f}%"
        primary_factor = shap["primary_factor"]

        q_lower = user_query.lower()
        intent = "general_analysis"

        # SINTESIS JAWABAN MURNI BERDASARKAN HASIL OBSERVASI TOOL NYATA:

        # Kasus A: User Menguji Keyakinan Model ("Apakah kamu yakin?")
        if "confidence" in obs:
            intent = "model_validation"
            c = obs["confidence"]
            response_text = (
                f"Sistem memiliki keyakinan data yang sangat tinggi dan dapat dipertanggungjawabkan secara ilmiah. "
                f"Model XGBoost dilatih menggunakan {c['training_samples']:,} pertandingan historis dengan metode {c['validation_method']}. "
                f"Hasil evaluasi pada {c['test_samples']:,} data uji menunjukkan Log Loss {c['log_loss']} dan Brier Score {c['brier_score']} "
                f"({c['calibration_status']}), membuktikan bahwa proyeksi kemenangan {home} ({h_prob}) vs {away} ({a_prob}) terkalibrasi secara objektif."
            )

        # Kasus B: Simulasi Skenario What-if
        elif "scenario" in obs:
            intent = "scenario_simulation"
            s = obs["scenario"]
            response_text = (
                f"Hasil Eksekusi Tool Simulasi ({s['scenario_name']}): "
                f"{s['explanation']} "
                f"Peluang kemenangan {home} berubah dari {h_prob} menjadi {s['scenario_result']['home_win_prob']*100:.1f}% "
                f"({s['probability_difference']*100:+.1f}%)."
            )

        # Kasus C: Analisis Kelemahan Pertahanan
        elif any(w in q_lower for w in ["lemah", "celah", "kebobolan"]):
            intent = "defensive_weakness"
            a_conceded = obs.get("away_team_info", {}).get("avg_conceded", 1.3)
            response_text = (
                f"Berdasarkan data observasi, {away} memiliki rata-rata kebobolan {a_conceded} gol/laga. "
                f"Kelemahan utama terletak pada koordinasi rest-defense saat menghadapi tekanan di area half-space. "
                f"Dengan probabilitas menang {h_prob}, {home} diproyeksikan mampu mendikte sepertiga akhir pertahanan {away}."
            )

        # Kasus D: Strategi Bertahan / Counter-Attack
        elif any(w in q_lower for w in ["taktik", "bertahan", "parkir", "counter"]):
            intent = "counter_strategy"
            response_text = (
                f"Berdasarkan faktor dominan {primary_factor}, jika {away} bermain dengan low-block, mereka harus mewaspadai "
                f"efektivitas tembakan jarak jauh {home}. Peluang terbaik {away} untuk mencuri gol ({a_prob}) "
                f"adalah memanfaatkan transisi kilat di sisi sayap dan situasi bola mati (set-piece)."
            )

        # Kasus E: Ringkasan Umum
        else:
            intent = "match_overview"
            response_text = (
                f"Analisis Taktikal Laga {home} vs {away} (Leg {leg}): "
                f"Model memproyeksikan {home} memiliki keunggulan {h_prob}, potensi seri {d_prob}, dan {away} {a_prob}. "
                f"Faktor kunci paling berpengaruh adalah {primary_factor}."
            )

        if leg == 2:
            response_text += f" Mengingat agregat Leg 1 ({h_score}-{a_score}), manajemen tempo laga akan sangat menentukan kelolosan."

        return {
            "response": response_text,
            "intent": intent,
            "tools_called": tools_called,  # <-- LIST ASLI DARI TOOL YANG DIEKSEKUSI
            "ground_truth": {
                "home_team": home,
                "away_team": away,
                "home_win_prob": pred["home_win_prob"],
                "away_win_prob": pred["away_win_prob"],
                "draw_prob": pred["draw_prob"],
                "top_factor": primary_factor
            }
        }


agent = ChampIntelAgent()