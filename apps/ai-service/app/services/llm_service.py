class LLMExplanationService:
    def __init__(self):
        print(">>> LLM Explanation Service aktif (Mode Ringan & Cepat) <<<")

    def generate_explanation(self, home_team: str, away_team: str, probs: dict, top_factors: list, leg: int, agg_text: str = "") -> str:
        home_pct = f"{probs['home_win_prob']*100:.1f}%"
        draw_pct = f"{probs['draw_prob']*100:.1f}%"
        away_pct = f"{probs['away_win_prob']*100:.1f}%"

        # Format faktor SHAP menjadi kalimat yang mudah dibaca
        factors_desc = ""
        if top_factors:
            primary_factor = top_factors[0]['feature']
            impact_type = "mendukung positif" if top_factors[0]['impact'] == 'positif' else "memberikan tekanan negatif"
            factors_desc = f"Faktor paling dominan yang memengaruhi jalannya laga adalah {primary_factor} yang {impact_type}."

        analysis = (
            f"Analisis Taktikal AI (ChampIntel Engine): "
            f"Berdasarkan pemodelan probabilitas XGBoost untuk leg ke-{leg}, "
            f"laga antara {home_team} dan {away_team} menunjukkan estimasi peluang kemenangan kandang {home_pct}, "
            f"seri {draw_pct}, dan kemenangan tandang {away_pct}. "
            f"{factors_desc} {agg_text}"
        )
        
        return analysis

llm_service = LLMExplanationService()