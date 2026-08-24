import os
import sys
from app.services.predictor import predictor
from app.services.llm_service import llm_service


class ChampIntelAgent:
    def __init__(self):
        print(">>> 🧠 ChampIntel Context-Augmented Agent SIAP Beroperasi! <<<")

    def run(self, user_query: str, match_data: dict, chat_history: list = None) -> dict:
        home_team = match_data.get("home_team", "Real Madrid")
        away_team = match_data.get("away_team", "Bayern Munich")
        leg = match_data.get("match_leg", 1)
        h_leg1 = match_data.get("home_leg1_score", 0)
        a_leg1 = match_data.get("away_leg1_score", 0)

        # 1. Tarik Data Ground Truth dari XGBoost & True Elo via predict_raw()
        raw_pred = predictor.predict_raw(match_data)
        h_prob = raw_pred.get("home_win_prob", 0.5) * 100
        d_prob = raw_pred.get("draw_prob", 0.25) * 100
        a_prob = raw_pred.get("away_win_prob", 0.25) * 100
        top_factors = raw_pred.get("top_factors", [])
        primary_factor = top_factors[0]["feature"] if top_factors else "Keseimbangan ELO"

        # 2. Deteksi Intent & Bangun Analisis Grounded (Bebas Halusinasi)
        q_lower = user_query.lower()
        intent = "general_tactical"

        if "lemah" in q_lower or "celah" in q_lower or "kebobolan" in q_lower:
            intent = "defensive_weakness"
            response_text = (
                f"Berdasarkan analisis statistik XGBoost, kelemahan yang dapat dieksploitasi terletak pada "
                f"koordinasi rest-defense {away_team}. Mengingat probabilitas kemenangan {home_team} mencapai {h_prob:.1f}%, "
                f"tuan rumah diproyeksikan akan menekan area half-space untuk memancing pelanggaran di sepertiga akhir pertahanan {away_team}."
            )
        elif "taktik" in q_lower or "bertahan" in q_lower or "parkir bus" in q_lower or "counter" in q_lower:
            intent = "counter_strategy"
            response_text = (
                f"Jika {away_team} memilih bermain dengan blok pertahanan rendah (low-block), mereka wajib mewaspadai faktor {primary_factor}. "
                f"Peluang terbaik {away_team} untuk mencuri gol (probabilitas {a_prob:.1f}%) adalah memaksimalkan transisi serangan balik cepat "
                f"dan situasi bola mati (set-piece)."
            )
        elif "pemain" in q_lower or "kunci" in q_lower or "duel" in q_lower:
            intent = "key_matchup"
            response_text = (
                f"Kunci duel {home_team} vs {away_team} ada pada perebutan lini sentral (holding midfielder). "
                f"Dengan selisih probabilitas {abs(h_prob - a_prob):.1f}%, siapapun yang memenangkan perebutan bola kedua (second balls) "
                f"akan mengontrol tempo dan ritme pertandingan."
            )
        elif "skenario" in q_lower or "agresif" in q_lower or "what if" in q_lower or "netral" in q_lower:
            intent = "scenario_simulation"
            sim = predictor.simulate_scenario(match_data, "aggressive_tactic")
            response_text = (
                f"Simulasi Skenario: Menerapkan taktik all-out attack akan mendongkrak probabilitas kemenangan {home_team} "
                f"dari {h_prob:.1f}% menjadi {sim['scenario_result']['home_win_prob']*100:.1f}% ({sim['probability_difference']*100:+.1f}%). "
                f"Namun, taktik ini meningkatkan risiko kebobolan gol tandang lewat serangan balik."
            )
        else:
            intent = "match_overview"
            response_text = (
                f"Menanggapi pertanyaan Anda seputar laga {home_team} vs {away_team} (Leg {leg}): "
                f"Pemodelan probabilitas XGBoost memproyeksikan {home_team} {h_prob:.1f}%, Seri {d_prob:.1f}%, dan {away_team} {a_prob:.1f}%. "
                f"Faktor dominan penentu laga adalah {primary_factor}. Kunci utama kedua tim adalah disiplin posisi pada 15 menit awal babak pertama."
            )

        if leg == 2:
            response_text += f" Mengingat skor Leg 1 ({h_leg1}-{a_leg1}), manajemen risiko dan waktu akan sangat krusial hingga peluit panjang."

        return {
            "response": response_text,
            "intent": intent,
            "ground_truth": {
                "home_team": home_team,
                "away_team": away_team,
                "home_win_prob": round(h_prob / 100, 2),
                "away_win_prob": round(a_prob / 100, 2),
                "draw_prob": round(d_prob / 100, 2),
                "top_factor": primary_factor
            }
        }


agent = ChampIntelAgent()