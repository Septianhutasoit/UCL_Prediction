 import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class LLMExplanationService:
    def __init__(self):
        self.pipe = None
        try:
            print("Memuat model Qwen2.5-1.5B-Instruct untuk penjelasan AI (mohon tunggu)...")
            model_id = "Qwen/Qwen2.5-1.5B-Instruct"
            
            # Load tokenizer & model (menggunakan float16 agar ramah RAM 16GB)
            self.tokenizer = AutoTokenizer.from_pretrained(model_id)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto"
            )
            
            self.pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=180,
                temperature=0.7,
            )
            print(">>> Model Qwen LLM BERHASIL dimuat untuk analisis taktik! <<<")
        except Exception as e:
            print(f"⚠️ Gagal memuat Qwen LLM (menggunakan template fallback): {e}")

    def generate_explanation(self, home_team: str, away_team: str, probs: dict, top_factors: list, leg: int, agg_text: str = "") -> str:
        if not self.pipe:
            # Fallback jika model gagal di-load (misal kendala RAM/koneksi)
            return f"Analisis AI (Template): Pertandingan antara {home_team} dan {away_team} (Leg {leg}) menghasilkan peluang menang kandang {probs['home_win_prob']*100:.1f}%. {agg_text}"

        prompt = f"""
        Kamu adalah analis taktik sepak bola UEFA Champions League. Buatlah ringkasan analisis pertandingan yang objektif, profesional, dan mengalir dalam bahasa Indonesia berdasarkan data berikut:
        - Pertandingan: {home_team} vs {away_team} (Leg {leg})
        - Probabilitas XGBoost: {home_team} Menang ({probs['home_win_prob']*100:.1f}%), Seri ({probs['draw_prob']*100:.1f}%), {away_team} Menang ({probs['away_win_prob']*100:.1f}%)
        - Faktor Penentu Utama (SHAP): {', '.join([f"{f['feature']} ({f['impact']})" for f in top_factors])}
        - Konteks Agregat: {agg_text}

        Aturan: Jangan membuat statistik baru di luar data ini. Berikan penjelasan taktis yang ringkas dan padat.
        """

        messages = [
            {"role": "system", "content": "Kamu adalah analis taktik sepak bola profesional."},
            {"role": "user", "content": prompt}
        ]
        
        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        outputs = self.pipe(text)
        generated_text = outputs[0]["generated_text"]
        
        # Ambil hasil setelah role assistant
        response = generated_text.split("assistant\n")[-1].strip()
        return response

llm_service = LLMExplanationService()
