import os


class LLMExplanationService:
    def __init__(self):
        print(">>> 🎙️ ChampIntel Hybrid Tactical Synthesizer AKTIF! <<<")

    def generate_explanation(
        self, 
        home_team: str, 
        away_team: str, 
        probs: dict, 
        top_factors: list, 
        leg: int, 
        agg_text: str = ""
    ) -> str:
        """Kompatibilitas lama untuk predictor.py"""
        h_prob = probs.get("home_win_prob", 0.5)
        d_prob = probs.get("draw_prob", 0.25)
        a_prob = probs.get("away_win_prob", 0.25)
        factor_desc = top_factors[0]['feature'] if top_factors else "Keseimbangan ELO"

        return (
            f"Berdasarkan pemodelan probabilitas XGBoost untuk Leg ke-{leg}, "
            f"{home_team} memiliki estimasi peluang menang {h_prob*100:.1f}%, seri {d_prob*100:.1f}%, dan {away_team} {a_prob*100:.1f}%. "
            f"Faktor dominan yang memengaruhi prediksi ini adalah {factor_desc}. {agg_text}"
        )

    # =========================================================================
    # 🧠 TAHAP 2: NATURAL LANGUAGE SYNTHESIZER (Untuk Agent Tahap 2)
    # =========================================================================
    def synthesize_response(
        self, 
        user_query: str, 
        intent: str, 
        ground_truth: dict, 
        chat_history: list = None
    ) -> str:
        """
        Menyusun narasi taktis bahasa alami dari paket fakta keras (Ground Truth) 
        secara dinamis untuk semua kombinasi tim sepak bola.
        """
        home = ground_truth["match_info"]["home_team"]
        away = ground_truth["match_info"]["away_team"]
        probs = ground_truth["probabilities"]
        h_prob = probs["home_win_prob"]
        d_prob = probs["draw_prob"]
        a_prob = probs["away_win_prob"]
        
        primary_factor = ground_truth.get("primary_factor", "Keseimbangan ELO")
        elo_info = ground_truth.get("elo", {})
        elo_diff = elo_info.get("difference", 0.0)
        h_elo = elo_info.get("home", 1500.0)
        a_elo = elo_info.get("away", 1500.0)

        form = ground_truth.get("form", {})
        h_sc = form.get("home_scored", 1.4)
        h_cc = form.get("home_conceded", 1.2)
        a_sc = form.get("away_scored", 1.2)
        a_cc = form.get("away_conceded", 1.2)
        h_pts = form.get("home_points_5", 7)
        a_pts = form.get("away_points_5", 6)

        # 1. Respons Sumber Data & Keyakinan Ilmiah Model
        if intent == "model_validation":
            c = ground_truth.get("scientific_metrics", {})
            return (
                f"📊 **Validitas & Landasan Ilmiah Model ({home} vs {away})**\n\n"
                f"• **Basis Data Historis:** Model XGBoost dilatih pada **{c.get('training_samples', 20783):,} pertandingan** Eropa dengan validasi *{c.get('validation_method', 'Temporal Split')}*.\n"
                f"• **Metrik Ilmiah:** Log Loss **{c.get('log_loss', 1.0022)}** & Brier Score **{c.get('brier_score', 0.5992)}** (*{c.get('calibration_status', 'Well-Calibrated')}*).\n"
                f"• **Konteks Duel:** Selisih True Elo sebesar **{elo_diff:+.1f} poin** ({home} {h_elo} vs {away} {a_elo}) menjadi dasar perhitungan probabilitas {home} ({h_prob}) vs {away} ({a_prob}) secara objektif."
            )

        # 2. Respons Simulasi Skenario What-if
        elif intent == "scenario_simulation":
            s = ground_truth.get("scenario", {})
            return (
                f"⚡ **Hasil Simulasi Taktikal: {home} vs {away}**\n\n"
                f"• **Skenario:** *{s.get('scenario_name', 'Taktik Agresif')}*\n"
                f"• **Pergeseran Probabilitas:** Peluang menang **{home}** bergeser dari **{h_prob} ➔ {s.get('scenario_result', {}).get('home_win_prob', 0.5)*100:.1f}%** ({s.get('probability_difference', 0.12)*100:+.1f}%).\n"
                f"• **Konsekuensi Taktis:** {s.get('explanation', '')} Mengingat produktivitas {home} ({h_sc} gol/laga), skenario ini menaikkan ancaman serangan namun menguji ketahanan rest-defense terhadap serangan balik {away} ({a_sc} gol/laga)."
            )

        # 3. Respons Celah & Kerapuhan Pertahanan
        elif intent == "defensive_weakness":
            return (
                f"🔍 **Analisis Celah Pertahanan {away}**\n\n"
                f"• **Statistik Kebobolan:** {away} mencatatkan rata-rata kemasukan **{a_cc} gol/laga** (Poin Form 5 Laga: {a_pts}/15).\n"
                f"• **Titik Rawan:** Koordinasi lini belakang {away} rentan mengalami *spatial overload* saat lawan menekan di area half-space.\n"
                f"• **Peluang {home}:** Dengan rata-rata mencetak **{h_sc} gol/laga** dan probabilitas menang {h_prob}, {home} diproyeksikan menekan sejak awal untuk memecah konsentrasi pertahanan {away}."
            )

        # 4. Respons Strategi Bertahan & Counter Attack
        elif intent == "counter_strategy":
            return (
                f"🛡️ **Strategi Bertahan & Transisi {away}**\n\n"
                f"• **Pendekatan Ideal:** Menghadapi dominasi {home} yang dipicu faktor *{primary_factor}*, opsi paling realistis bagi {away} adalah blok pertahanan *medium-to-low*.\n"
                f"• **Peluang Gol ({a_prob}):** Memaksimalkan kecepatan transisi *turnover* sayap (rata-rata gol tandang: {a_sc}) dan efisiensi bola mati (*set-piece*).\n"
                f"• **Kunci Sukses:** Menghindari pelanggaran di sepertiga akhir lapangan pada 15 menit awal babak pertama."
            )

        # 5. Respons Duel Kunci / Lini Sentral
        elif intent == "key_matchup":
            return (
                f"⚔️ **Pertarungan Kunci & Poros Lini Tengah ({home} vs {away})**\n\n"
                f"• **Perbandingan Skuad:** {home} (Elo: {h_elo} | Form: {h_pts} pts) vs {away} (Elo: {a_elo} | Form: {a_pts} pts).\n"
                f"• **Duel Sentral:** Titik tumpu laga berada pada perebutan *second balls* di posisi gelandang jangkar (*holding midfielder*).\n"
                f"• **Proyeksi:** Tim yang memenangkan kontrol transisi lini tengah akan langsung mengamankan tempo pertandingan."
            )

        # 6. Respons Analisis Umum
        else:
            return (
                f"📋 **Analisis Taktikal Menyeluruh: {home} vs {away}**\n\n"
                f"• **Estimasi Hasil:** {home} **{h_prob}** | Seri **{d_prob}** | {away} **{a_prob}**.\n"
                f"• **Faktor Kunci SHAP:** Keunggulan laga ini didorong kuat oleh faktor *{primary_factor}* (Selisih True Elo: **{elo_diff:+.1f} poin**).\n"
                f"• **Catatan Pelatih:** Disiplin menjaga struktur formasi pada 15 menit awal babak pertama akan menjadi penentu ritme laga."
            )


llm_service = LLMExplanationService()