import os


class LLMExplanationService:
    def __init__(self):
        print(">>> 🎙️ ChampIntel Tactical Commentary Engine AKTIF (Mode Super Cepat & Stabil) <<<")

    def generate_explanation(
        self, 
        home_team: str, 
        away_team: str, 
        probs: dict, 
        top_factors: list, 
        leg: int, 
        agg_text: str = ""
    ) -> str:
        """Menghasilkan analisis taktik mendalam, objektif, dan berbobot komentator profesional."""
        h_prob = probs.get("home_win_prob", 0.5)
        d_prob = probs.get("draw_prob", 0.25)
        a_prob = probs.get("away_win_prob", 0.25)

        h_pct = f"{h_prob*100:.1f}%"
        d_pct = f"{d_prob*100:.1f}%"
        a_pct = f"{a_prob*100:.1f}%"

        factor_names = [f["feature"] for f in top_factors[:2]] if top_factors else ["kualitas taktik"]
        primary_factor = factor_names[0] if factor_names else "keseimbangan permainan"

        # 1. Analisis Taktikal Multi-Sudut Pandang
        if h_prob >= a_prob + 0.10:
            intro = (
                f"Dalam duel Leg ke-{leg} ini, {home_team} memegang inisiatif taktikal dengan keunggulan "
                f"probabilitas kemenangan sebesar {h_pct}, berbanding {a_pct} untuk {away_team} dan {d_pct} potensi seri."
            )
            tactics = (
                f"Dominasi {home_team} didorong kuat oleh faktor {primary_factor}, yang memungkinkan mereka "
                f"menerapkan high-pressing intensif dan mengontrol tempo permainan di lini tengah sejak menit awal."
            )
            defense = (
                f"{away_team} diproyeksikan akan dipaksa bermain lebih reaktif dengan blok pertahanan rendah, "
                f"sembari mencari celah transisi serangan balik cepat."
            )
        elif a_prob >= h_prob + 0.10:
            intro = (
                f"Meskipun bertindak sebagai tim tamu pada Leg ke-{leg}, {away_team} justru menunjukkan proyeksi "
                f"keunggulan yang lebih dominan ({a_pct} vs {h_pct} milik {home_team})."
            )
            tactics = (
                f"Efektivitas {primary_factor} menjadi pembeda krusial, di mana struktur transisi {away_team} "
                f"sangat berbahaya dalam mengeksploitasi ruang di sepertiga akhir pertahanan tuan rumah."
            )
            defense = (
                f"{home_team} wajib menjaga kedisiplinan rest-defense agar tidak kecolongan gol tandang yang fatal."
            )
        else:
            intro = (
                f"Pertandingan Leg ke-{leg} antara {home_team} dan {away_team} diproyeksikan berlangsung sangat ketat "
                f"dan berimbang, dengan estimasi probabilitas {home_team} {h_pct}, seri {d_pct}, dan {away_team} {a_pct}."
            )
            tactics = (
                f"Kedua tim memiliki margin kekuatan yang sangat tipis, di mana pengaruh {primary_factor} "
                f"akan menjadi kunci penentu dalam memecah kebuntuan duel lini sentral."
            )
            defense = (
                f"Fokus mental dan efisiensi konversi peluang akan menjadi penentu tipis siapa yang keluar sebagai pemenang."
            )

        agg_summary = f" {agg_text}" if agg_text else ""
        
        return f"{intro} {tactics} {defense}{agg_summary}"


llm_service = LLMExplanationService()