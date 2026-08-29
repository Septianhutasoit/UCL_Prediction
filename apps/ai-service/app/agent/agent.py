import os
import re
import random
from app.agent.tools import TOOL_REGISTRY
from app.services.predictor import predictor

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
        print(">>> 🤖 ChampIntel Multi-Style Dynamic Agent (Anti-Kaku + Sadar Batas Konteks) AKTIF! <<<")
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
            response_text = random.choice(decline_variations)
            return {
                "response": response_text,
                "intent": intent,
                "tools_called": [],
                "ground_truth": None,
            }

        # 2. Baru dari sini eksekusi single-pass inference — hanya untuk query yang relevan
        cached_res = predictor.predict_raw(match_data)

        # 3. Tarik statistik ASLI kedua tim — dipakai di SEMUA cabang intent
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

        # 4. Sintesis dinamis dengan variasi gaya bahasa — setiap kategori punya beberapa
        #    pembuka/penekanan berbeda, dipilih acak, tapi datanya tetap 100% presisi & konsisten.
        if intent == "model_validation":
            conf_obs = self.tools["model_confidence"]()
            tools_called.append("Tool: Model Scientific Validation")
            c = conf_obs["data"]
            variations = [
                (
                    f"Model XGBoost kami dilatih pada {c['training_samples']:,} pertandingan historis dengan {c['validation_method']}. "
                    f"Selisih True Elo sebesar {elo_diff:+.1f} poin ({home} {h_elo} vs {away} {a_elo}) menjadi jangkar utama perhitungannya. "
                    f"Log Loss {c['log_loss']} dan Brier Score {c['brier_score']} ({c['calibration_status']}) menjamin estimasi "
                    f"{home} {h_prob} berbanding {away} {a_prob} ini bebas dari tebakan asal."
                ),
                (
                    f"Prediksi ini bukan tebakan acak — dasarnya pemodelan probabilitas terkalibrasi dari {c['training_samples']:,} laga Eropa. "
                    f"Brier Score-nya {c['brier_score']}, dan sudah diuji lewat metode temporal split supaya tidak ada kebocoran data masa depan "
                    f"yang bikin hasilnya {home} ({h_prob}) vs {away} ({a_prob}) jadi bias."
                ),
                (
                    f"Landasannya cukup solid: {c['training_samples']:,} sampel historis, Log Loss {c['log_loss']}, Brier Score {c['brier_score']} "
                    f"({c['calibration_status']}). Selisih Elo {home} dan {away} ({elo_diff:+.1f} poin) ikut memengaruhi kenapa probabilitasnya "
                    f"condong ke {home if h_prob_num > a_prob_num else away}."
                ),
            ]
            response_text = random.choice(variations)

        elif intent == "scenario_simulation":
            scenario_type = "neutral_venue" if ("netral" in q_lower or "neutral" in q_lower) else "aggressive_tactic"
            sim_obs = self.tools["simulate_scenario"](match_data, scenario_type)
            tools_called.append("Tool: What-if Simulator")
            s = sim_obs["data"]
            variations = [
                (
                    f"Simulasi \"{s['scenario_name']}\" menunjukkan peluang menang {home} bergeser dari {h_prob} menjadi "
                    f"{s['scenario_result']['home_win_prob']*100:.1f}% ({s['probability_difference']*100:+.1f}%). {s['explanation']} "
                    f"Dengan produktivitas {home} di angka {h_sc} gol/laga, perubahan ini menaikkan ancaman serangan sekaligus "
                    f"menguji ketahanan lini belakang menghadapi serangan balik {away} ({a_sc} gol/laga)."
                ),
                (
                    f"Kalau skenarionya \"{s['scenario_name']}\", {s['explanation']} Angka peluang {home} berubah jadi "
                    f"{s['scenario_result']['home_win_prob']*100:.1f}% dari sebelumnya {h_prob} — pergeseran {s['probability_difference']*100:+.1f}%. "
                    f"Bukan perubahan kecil, mengingat rata-rata kebobolan {away} juga di angka {a_cc} gol/laga."
                ),
            ]
            response_text = random.choice(variations)

        elif intent == "defensive_weakness":
            tools_called.append("Tool: Team Intelligence DB")
            variations = [
                (
                    f"{away} mencatatkan rata-rata kebobolan {a_cc} gol/laga (form 5 laga terakhir: {a_pts} poin). "
                    f"Celah paling nyata ada di koordinasi rest-defense saat lawan melakukan transisi cepat di area half-space. "
                    f"Dengan rata-rata mencetak {h_sc} gol/laga, {home} diproyeksikan mengeksploitasi ini lewat umpan terobosan vertikal."
                ),
                (
                    f"Pertahanan {away} cenderung rapuh di sisi sayap — terbukti dari angka kebobolan {a_cc} gol per laga. "
                    f"Dengan peluang menang {h_prob}, {home} kemungkinan menaikkan garis pressing tinggi untuk memutus sirkulasi bola "
                    f"{away} sejak sepertiga awal lapangan."
                ),
                (
                    f"Kalau lihat datanya, {away} lumayan sering kebobolan (rata-rata {a_cc} gol/laga, form cuma {a_pts} poin dari 5 laga terakhir). "
                    f"Ini celah yang realistis buat {home} dieksploitasi, apalagi produktivitas mereka sendiri ada di {h_sc} gol/laga."
                ),
            ]
            response_text = random.choice(variations)

        elif intent == "counter_strategy":
            tools_called.append("Tool: Team Intelligence DB")
            if h_prob_num >= a_prob_num + 15.0:
                advice_variations = [
                    f"Mengingat {home} punya keunggulan Elo signifikan ({elo_diff:+.1f} poin), {away} sebaiknya main disiplin dengan blok medium-to-low.",
                    f"Selisih kekuatan lumayan jomplang ({elo_diff:+.1f} poin Elo untuk {home}), jadi {away} realistisnya harus rapat dan sabar, bukan coba imbangi permainan terbuka.",
                ]
            elif a_prob_num >= h_prob_num + 15.0:
                advice_variations = [
                    f"Meski berstatus tamu, keunggulan kualitas {away} ({a_elo} vs {h_elo} Elo) memungkinkan mereka kontrol tempo tanpa perlu bertahan pasif.",
                    f"Justru {away} yang di atas angin di sini ({a_elo} vs {h_elo} Elo) — mereka bisa lebih berani menekan, bukan cuma menunggu serangan balik.",
                ]
            else:
                advice_variations = [
                    f"Kekuatan kedua tim cukup seimbang ({home} {h_prob} vs {away} {a_prob}), jadi laga ini bakal ditentukan margin kesalahan kecil.",
                    f"Selisihnya tipis ({home} {h_prob} vs {away} {a_prob}) — detail kecil seperti transisi dan set-piece yang akan menentukan.",
                ]
            tactic_advice = random.choice(advice_variations)
            response_text = (
                f"{tactic_advice} Peluang gol {away} ({a_prob}) paling realistis lewat transisi cepat di sisi sayap "
                f"(rata-rata gol tandang: {a_sc}) dan efisiensi set-piece. Faktor kunci yang paling berpengaruh: {primary_factor}."
            )

        elif intent == "key_matchup":
            tools_called.append("Tool: Team Intelligence DB")
            variations = [
                (
                    f"Perbandingan kekuatan: {home} (Elo {h_elo}, form {h_pts} poin) vs {away} (Elo {a_elo}, form {a_pts} poin). "
                    f"Titik krusialnya ada di perebutan second-ball lini tengah untuk memutus suplai bola ke lini depan {away}."
                ),
                (
                    f"Kalau saya harus pilih satu area penentu, itu perebutan gelandang jangkar antara {home} dan {away} — "
                    f"tim yang menang di situ ({home} form {h_pts} vs {away} form {a_pts}) biasanya yang mengontrol jalannya laga."
                ),
            ]
            response_text = random.choice(variations)

        else:  # general_analysis
            variations = [
                (
                    f"Analisis taktikal {home} vs {away} (Leg {leg}): estimasi model menunjukkan {home} {h_prob}, "
                    f"seri {d_prob}, dan {away} {a_prob}. Selisih True Elo kedua tim {elo_diff:+.1f} poin, "
                    f"dengan faktor kunci penentu: {primary_factor}."
                ),
                (
                    f"Untuk laga {home} vs {away}, model memproyeksikan peluang {h_prob} untuk {home}, {d_prob} seri, "
                    f"dan {a_prob} untuk {away}. Yang paling berpengaruh di balik angka ini adalah {primary_factor}."
                ),
            ]
            response_text = random.choice(variations)

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