import os
import json
import random


try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


class LLMExplanationService:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_dir = os.path.join(base_dir, "models", "ucl_qwen_adapter")

        self.model = None
        self.tokenizer = None
        self.device = "cuda" if (TORCH_AVAILABLE and torch.cuda.is_available()) else "cpu"

        if TORCH_AVAILABLE:
            self._init_local_llm()
        else:
            print(">>> 🎙️ ChampIntel Tactical Synthesizer aktif (mode ringan — torch belum terpasang) <<<")

    def _init_local_llm(self):
        """Muat model neural HANYA jika ada GPU CUDA. Jika di CPU laptop, pakai Dynamic Synthesis agar tidak crash memori."""
        try:
            # Hanya muat model 3GB jika ada GPU CUDA asli (mencegah Windows CPU Memory Crash)
            if self.device == "cuda" and os.path.exists(self.model_dir) and os.path.exists(os.path.join(self.model_dir, "config.json")):
                print(f">>> 🤖 Memuat Qwen 2.5 Generative Engine dari {self.model_dir} (GPU)... <<<")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_dir,
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
                print(">>> ✅ Model Qwen 2.5 Generative Engine AKTIF di GPU! <<<")
            else:
                # Di CPU laptop: aktifkan Dynamic Synthesis Engine (Super Cepat < 2ms & Bebas Crash)
                print(">>> 🎙️ ChampIntel Tactical Synthesizer aktif (Mode Dynamic Synthesis Cepat & Stabil) <<<")
                self.model = None
                self.tokenizer = None
        except Exception as e:
            print(f">>> ℹ️ Dynamic Synthesis Fallback aktif ({e}) <<<")
            self.model = None
            self.tokenizer = None

    # =========================================================================
    # Kompatibilitas lama — dipakai predictor.py untuk endpoint /predict biasa
    # (di luar alur agent/chat). JANGAN dihapus, masih dipakai.
    # =========================================================================
    def generate_explanation(
        self,
        home_team: str,
        away_team: str,
        probs: dict,
        top_factors: list,
        leg: int,
        agg_text: str = "",
    ) -> str:
        h_prob = probs.get("home_win_prob", 0.5)
        d_prob = probs.get("draw_prob", 0.25)
        a_prob = probs.get("away_win_prob", 0.25)
        factor_desc = top_factors[0]["feature"] if top_factors else "keseimbangan Elo kedua tim"

        variations = [
            (
                f"Berdasarkan pemodelan probabilitas XGBoost untuk Leg ke-{leg}, {home_team} punya estimasi peluang menang "
                f"{h_prob*100:.1f}%, seri {d_prob*100:.1f}%, dan {away_team} {a_prob*100:.1f}%. Faktor dominan di balik "
                f"prediksi ini adalah {factor_desc}. {agg_text}"
            ),
            (
                f"Model memproyeksikan laga Leg {leg} ini condong ke {home_team} dengan peluang {h_prob*100:.1f}% "
                f"(seri {d_prob*100:.1f}%, {away_team} {a_prob*100:.1f}%), didorong terutama oleh {factor_desc}. {agg_text}"
            ),
        ]
        return random.choice(variations).strip()

    # =========================================================================
    # 🧠 TAHAP 2: NATURAL LANGUAGE SYNTHESIZER — dipanggil agent.py
    # =========================================================================
    def _build_grounded_prompt(self, user_query: str, intent: str, gt: dict) -> tuple[str, str]:
        """Bangun system + user prompt dengan Context Injection (Grounded RAG) — angka dikunci, tidak boleh diubah LLM."""
        home = gt["match_info"]["home_team"]
        away = gt["match_info"]["away_team"]
        leg = gt["match_info"]["match_leg"]
        probs = gt["probabilities"]
        primary_factor = gt.get("primary_factor", "keseimbangan Elo kedua tim")
        elo = gt.get("elo", {})
        form = gt.get("form", {})

        system_prompt = (
            "Kamu adalah analis taktik sepak bola UEFA Champions League profesional. Jawab pertanyaan pengguna secara "
            "ramah, analitis, dan mengalir alami seperti manusia — bukan seperti mengisi formulir. ATURAN MUTLAK:\n"
            "1. Selalu gunakan fakta dan angka pada DATA GROUND TRUTH di bawah sebagai dasar argumen.\n"
            "2. JANGAN PERNAH mengubah, membulatkan ulang, atau mengarang angka probabilitas.\n"
            "3. Gunakan istilah sepak bola modern secukupnya (half-space, rest-defense, high-pressing, low-block, set-piece).\n"
            "4. Tulis dalam paragraf mengalir, PLAIN TEXT — jangan pakai markdown (tanpa tanda bintang **, tanpa bullet "
            "point •, tanpa heading), karena akan ditampilkan sebagai teks polos di chat.\n"
            "5. Kalau pertanyaan pengguna ada typo atau tidak baku, tetap pahami maksudnya dan jawab dengan sopan."
        )

        context_data = {
            "pertandingan": f"{home} vs {away} (Leg {leg})",
            "probabilitas_xgboost": {
                "menang_kandang": probs["home_win_prob"],
                "seri": probs["draw_prob"],
                "menang_tandang": probs["away_win_prob"],
            },
            "faktor_kunci_shap": primary_factor,
            "rating_true_elo": {
                home: elo.get("home", 1500),
                away: elo.get("away", 1500),
                "selisih": elo.get("difference", 0),
            },
            "statistik_form_terkini": {
                f"{home}_memasukkan": form.get("home_scored", 1.4),
                f"{home}_kebobolan": form.get("home_conceded", 1.2),
                f"{away}_memasukkan": form.get("away_scored", 1.2),
                f"{away}_kebobolan": form.get("away_conceded", 1.3),
            },
        }
        if gt.get("scientific_metrics"):
            context_data["bukti_validasi_model"] = gt["scientific_metrics"]
        if gt.get("scenario"):
            context_data["hasil_simulasi_skenario"] = gt["scenario"]

        user_content = (
            f"[DATA GROUND TRUTH RESMI]:\n{json.dumps(context_data, ensure_ascii=False, indent=2)}\n\n"
            f"[PERTANYAAN PENGGUNA]: {user_query}"
        )
        return system_prompt, user_content

    def synthesize_response(self, user_query: str, intent: str, ground_truth: dict, chat_history: list = None) -> str:
        """
        Tahap 2: kalau model Qwen neural aktif, lakukan generative inference asli.
        Kalau tidak (belum di-load / gagal / hasil terlalu pendek), pakai Dynamic
        Synthesis Fallback — tetap kaya variasi & berbasis data, TIDAK PERNAH crash.
        """
        if self.model is not None and self.tokenizer is not None and TORCH_AVAILABLE:
            try:
                system_prompt, prompt_content = self._build_grounded_prompt(user_query, intent, ground_truth)
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt_content},
                ]
                text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

                with torch.no_grad():
                    gen = self.model.generate(
                        **inputs,
                        max_new_tokens=220,
                        temperature=0.4,
                        top_p=0.9,
                        do_sample=True,
                    )
                result = self.tokenizer.batch_decode(gen[:, inputs.input_ids.shape[1]:], skip_special_tokens=True)[0].strip()

                # Jaga stabilitas: hasil generasi yang terlalu pendek/kosong dianggap gagal, jatuh ke fallback
                if len(result) >= 15:
                    return result
                print("⚠️ Hasil generasi neural terlalu pendek, pakai fallback.")
            except Exception as e:
                print(f"⚠️ Neural generation gagal, pakai fallback ({e})")

        return self._dynamic_synthesis_fallback(intent, ground_truth)

    def _dynamic_synthesis_fallback(self, intent: str, gt: dict) -> str:
        """
        Penyusun narasi adaptif berbasis fakta ground truth, plain text, dengan
        beberapa variasi gaya bahasa per kategori (dipilih acak) supaya tidak kaku.
        """
        home = gt["match_info"]["home_team"]
        away = gt["match_info"]["away_team"]
        leg = gt["match_info"]["match_leg"]
        probs = gt["probabilities"]
        h_prob = f"{probs['home_win_prob']*100:.1f}%"
        d_prob = f"{probs['draw_prob']*100:.1f}%"
        a_prob = f"{probs['away_win_prob']*100:.1f}%"
        h_prob_num = probs["home_win_prob"] * 100
        a_prob_num = probs["away_win_prob"] * 100

        primary_factor = gt.get("primary_factor", "keseimbangan Elo kedua tim")
        elo = gt.get("elo", {})
        elo_diff = elo.get("difference", 0.0)
        h_elo = elo.get("home", 1500.0)
        a_elo = elo.get("away", 1500.0)

        form = gt.get("form", {})
        h_sc = form.get("home_scored", 1.4)
        h_cc = form.get("home_conceded", 1.2)
        a_sc = form.get("away_scored", 1.2)
        a_cc = form.get("away_conceded", 1.3)
        h_pts = form.get("home_points_5", 7)
        a_pts = form.get("away_points_5", 6)

        if intent == "model_validation":
            c = gt.get("scientific_metrics") or {}
            variations = [
                (
                    f"Model XGBoost kami dilatih pada {c.get('training_samples', 20783):,} pertandingan historis "
                    f"dengan {c.get('validation_method', 'temporal split')}. Selisih True Elo {elo_diff:+.1f} poin "
                    f"({home} {h_elo} vs {away} {a_elo}) jadi jangkar utama perhitungannya. Log Loss "
                    f"{c.get('log_loss', 1.0022)} dan Brier Score {c.get('brier_score', 0.5992)} "
                    f"({c.get('calibration_status', 'well-calibrated')}) menjamin estimasi {home} ({h_prob}) "
                    f"berbanding {away} ({a_prob}) ini bebas dari tebakan asal."
                ),
                (
                    f"Prediksi ini bukan tebakan acak — dasarnya pemodelan probabilitas terkalibrasi dari "
                    f"{c.get('training_samples', 20783):,} laga Eropa. Brier Score-nya {c.get('brier_score', 0.5992)}, "
                    f"sudah diuji lewat temporal split supaya tidak ada kebocoran data masa depan yang bikin hasil "
                    f"{home} ({h_prob}) vs {away} ({a_prob}) jadi bias."
                ),
            ]
            return random.choice(variations)

        if intent == "scenario_simulation":
            s = gt.get("scenario") or {}
            sc_result = s.get("scenario_result", {})
            variations = [
                (
                    f"Simulasi \"{s.get('scenario_name', 'skenario taktik')}\" menunjukkan peluang menang {home} "
                    f"bergeser dari {h_prob} menjadi {sc_result.get('home_win_prob', 0.5)*100:.1f}% "
                    f"({s.get('probability_difference', 0)*100:+.1f}%). {s.get('explanation', '')} Dengan produktivitas "
                    f"{home} di angka {h_sc} gol/laga, ini menaikkan ancaman serangan sekaligus menguji ketahanan lini "
                    f"belakang menghadapi serangan balik {away} ({a_sc} gol/laga)."
                ),
                (
                    f"Kalau skenarionya \"{s.get('scenario_name', 'skenario taktik')}\", {s.get('explanation', '')} "
                    f"Peluang {home} berubah jadi {sc_result.get('home_win_prob', 0.5)*100:.1f}% dari sebelumnya "
                    f"{h_prob} — pergeseran {s.get('probability_difference', 0)*100:+.1f}%, mengingat kebobolan "
                    f"{away} juga di angka {a_cc} gol/laga."
                ),
            ]
            return random.choice(variations)

        if intent == "defensive_weakness":
            variations = [
                (
                    f"{away} mencatatkan rata-rata kebobolan {a_cc} gol/laga (form 5 laga terakhir: {a_pts} poin). "
                    f"Celah paling nyata ada di koordinasi rest-defense saat lawan melakukan transisi cepat di area "
                    f"half-space. Dengan rata-rata mencetak {h_sc} gol/laga, {home} diproyeksikan mengeksploitasi ini "
                    f"lewat umpan terobosan vertikal."
                ),
                (
                    f"Pertahanan {away} cenderung rapuh di sisi sayap — terbukti dari angka kebobolan {a_cc} gol per "
                    f"laga. Dengan peluang menang {h_prob}, {home} kemungkinan menaikkan garis pressing tinggi untuk "
                    f"memutus sirkulasi bola {away} sejak sepertiga awal lapangan."
                ),
            ]
            return random.choice(variations)

        if intent == "counter_strategy":
            if h_prob_num >= a_prob_num + 15.0:
                advice = f"Mengingat {home} punya keunggulan Elo signifikan ({elo_diff:+.1f} poin), {away} sebaiknya main disiplin dengan blok medium-to-low."
            elif a_prob_num >= h_prob_num + 15.0:
                advice = f"Meski berstatus tamu, keunggulan kualitas {away} ({a_elo} vs {h_elo} Elo) memungkinkan mereka kontrol tempo tanpa perlu bertahan pasif."
            else:
                advice = f"Kekuatan kedua tim cukup seimbang ({home} {h_prob} vs {away} {a_prob}), jadi laga ini bakal ditentukan margin kesalahan kecil."
            return (
                f"{advice} Peluang gol {away} ({a_prob}) paling realistis lewat transisi cepat di sisi sayap "
                f"(rata-rata gol tandang: {a_sc}) dan efisiensi set-piece. Faktor kunci yang paling berpengaruh: {primary_factor}."
            )

        if intent == "key_matchup":
            variations = [
                (
                    f"Perbandingan kekuatan: {home} (Elo {h_elo}, form {h_pts} poin) vs {away} (Elo {a_elo}, form "
                    f"{a_pts} poin). Titik krusialnya ada di perebutan second-ball lini tengah untuk memutus suplai "
                    f"bola ke lini depan {away}."
                ),
                (
                    f"Kalau harus pilih satu area penentu, itu perebutan gelandang jangkar antara {home} dan {away} "
                    f"— tim yang menang di situ biasanya yang mengontrol jalannya laga."
                ),
            ]
            return random.choice(variations)

        variations = [
            (
                f"Analisis taktikal {home} vs {away} (Leg {leg}): estimasi model menunjukkan {home} {h_prob}, "
                f"seri {d_prob}, dan {away} {a_prob}. Selisih True Elo kedua tim {elo_diff:+.1f} poin, dengan faktor "
                f"kunci penentu: {primary_factor}."
            ),
            (
                f"Untuk laga {home} vs {away}, model memproyeksikan peluang {h_prob} untuk {home}, {d_prob} seri, "
                f"dan {a_prob} untuk {away}. Yang paling berpengaruh di balik angka ini adalah {primary_factor}."
            ),
        ]
        return random.choice(variations)


llm_service = LLMExplanationService()