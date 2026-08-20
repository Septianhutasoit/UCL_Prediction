from app.agent.tools import tool_predict_match, tool_get_match_stats, tool_simulate_what_if

class ChampIntelAgent:
    def __init__(self):
        print(">>> ChampIntel AI Agent (Orchestrator) siap beroperasi! <<<")

    def run_agent(self, user_query: str, home_team: str, away_team: str, match_leg: int = 1, home_leg1_score: int = 0, away_leg1_score: int = 0):
        query = user_query.lower().strip()
        
        # 1. Sapaan Murni (Hanya kata sapaan spesifik)
        exact_greetings = ["halo", "hola", "hai", "hi", "pagi", "siang", "malam", "p", "test"]
        if query in exact_greetings:
            return {
                "intent": "greeting",
                "response": f"🤖 Halo! Saya ChampIntel Analyst Agent. Silakan tanyakan analisis taktik untuk laga **{home_team}** vs **{away_team}**, atau uji skenario seperti *'Bagaimana jika main di tempat netral?'*.",
                "data": None
            }

        # 2. Pertanyaan Keraguan / Follow-up (Misal: "kamu yakin?", "kenapa?", "jelaskan")
        if any(w in query for w in ["yakin", "kenapa", "kok", "mengapa", "jelaskan", "bukti", "serius"]):
            prediction_res = tool_predict_match(home_team, away_team, match_leg, home_leg1_score, away_leg1_score)
            response_text = (
                f"🤖 Tentu! Prediksi ini didasarkan pada perhitungan statistik objektif dari 26.000 data historis, bukan asumsi.\n\n"
                f"• Peluang Menang ({home_team}): {prediction_res['home_win_prob']*100:.1f}%\n"
                f"• Peluang Seri: {prediction_res['draw_prob']*100:.1f}%\n"
                f"• Peluang Menang ({away_team}): {prediction_res['away_win_prob']*100:.1f}%\n\n"
                f"Alasan statistik: {prediction_res['ai_analysis']}"
            )
            return {
                "intent": "explanation",
                "response": response_text,
                "data": prediction_res
            }

        # 3. Deteksi Skenario What-if (Tempat Netral)
        if "netral" in query or "tanpa kandang" in query or "tandang" in query:
            sim_res = tool_simulate_what_if(home_team, away_team, "neutral_venue")
            diff_pct = sim_res.get('probability_difference', 0.0) * 100
            return {
                "intent": "simulation",
                "response": f"🤖 {sim_res['scenario_name']}\n\n{sim_res['explanation']}\n\n📊 Perubahan probabilitas kemenangan: {diff_pct:+.1f}%",
                "data": sim_res
            }
            
        # 4. Deteksi Skenario What-if (Taktik Agresif)
        elif "agresif" in query or "menyerang" in query or "all out" in query:
            sim_res = tool_simulate_what_if(home_team, away_team, "aggressive_tactic")
            diff_pct = sim_res.get('probability_difference', 0.0) * 100
            return {
                "intent": "simulation",
                "response": f"🤖 {sim_res['scenario_name']}\n\n{sim_res['explanation']}\n\n📊 Perubahan probabilitas kemenangan: {diff_pct:+.1f}%",
                "data": sim_res
            }

        # 5. Default Intent: Panggil tool prediksi utama
        detected_leg = match_leg
        if "leg 1" in query or "leg pertama" in query:
            detected_leg = 1
        elif "leg 2" in query or "leg kedua" in query:
            detected_leg = 2

        prediction_res = tool_predict_match(home_team, away_team, detected_leg, home_leg1_score, away_leg1_score)
        
        response_text = (
            f"🤖 Berdasarkan analisis Agent untuk laga {home_team} vs {away_team} (Leg {detected_leg}):\n\n"
            f"• Peluang Menang ({home_team}): {prediction_res['home_win_prob']*100:.1f}%\n"
            f"• Peluang Seri: {prediction_res['draw_prob']*100:.1f}%\n"
            f"• Peluang Menang ({away_team}): {prediction_res['away_win_prob']*100:.1f}%\n\n"
            f"{prediction_res['ai_analysis']}"
        )

        return {
            "intent": "prediction_with_explainability",
            "response": response_text,
            "data": prediction_res
        }

agent = ChampIntelAgent()