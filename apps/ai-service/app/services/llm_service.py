import os

# Cek ketersediaan PyTorch dan Transformers secara aman tanpa membuat server crash
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
        
        if TORCH_AVAILABLE:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.load_fine_tuned_model()
        else:
            print(">>> ℹ️ LLM Explanation Service aktif (Mode Ringan & Cepat) <<<")

    def load_fine_tuned_model(self):
        try:
            if os.path.exists(self.model_dir) and os.path.exists(os.path.join(self.model_dir, "model.safetensors")):
                print(f">>> 🤖 Memuat Qwen 2.5 Fine-Tuned dari: {self.model_dir} ({self.device}) <<<")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
                torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_dir,
                    torch_dtype=torch_dtype,
                    device_map="auto" if self.device == "cuda" else None,
                    low_cpu_mem_usage=True
                )
                if self.device == "cpu":
                    self.model.to("cpu")
                print(">>> ✅ Model Qwen 2.5 Fine-Tuned (ucl_qwen_adapter) BERHASIL aktif! <<<")
            else:
                print(">>> ℹ️ Folder ucl_qwen_adapter belum lengkap, beralih ke Mode Cepat. <<<")
        except Exception as e:
            print(f"⚠️ Gagal memuat model neural ({e}), menggunakan Mode Cepat.")
            self.model = None

    def generate_explanation(
        self, 
        home_team: str, 
        away_team: str, 
        probs: dict, 
        top_factors: list, 
        leg: int, 
        agg_text: str = ""
    ) -> str:
        h_prob = f"{probs['home_win_prob']*100:.1f}%"
        d_prob = f"{probs['draw_prob']*100:.1f}%"
        a_prob = f"{probs['away_win_prob']*100:.1f}%"
        
        factor_desc = top_factors[0]['feature'] if top_factors else "keseimbangan taktik"

        user_prompt = (
            f"Pertandingan: {home_team} vs {away_team}. Leg: {leg}. "
            f"Probabilitas: Home Win {h_prob}, Draw {d_prob}, Away Win {a_prob}. "
            f"Faktor Kunci: {factor_desc}. {agg_text}"
        )

        # 1. JIKA MODEL QWEN & TORCH TERPASANG (Neural AI Mode)
        if self.model is not None and self.tokenizer is not None and TORCH_AVAILABLE:
            try:
                messages = [
                    {
                        "role": "system",
                        "content": "Kamu adalah analis taktik sepak bola UEFA Champions League yang objektif, presisi terhadap data probabilitas, dan berbasis analisis numerik."
                    },
                    {"role": "user", "content": user_prompt}
                ]
                
                text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
                model_inputs = self.tokenizer([text], return_tensors="pt").to(self.device)

                with torch.no_grad():
                    generated_ids = self.model.generate(
                        **model_inputs,
                        max_new_tokens=150,
                        temperature=0.3,
                        do_sample=True,
                        top_p=0.9
                    )

                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]

                response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                return response.strip()
            except Exception as e:
                print(f"⚠️ Error saat neural generation ({e}), memakai fallback.")

        # 2. FALLBACK CEPAT (Respon Instan Tanpa Beban Laptop)
        return (
            f"Berdasarkan kalkulasi probabilitas XGBoost untuk Leg ke-{leg}, "
            f"{home_team} memiliki estimasi peluang menang {h_prob}, seri {d_prob}, dan {away_team} {a_prob}. "
            f"Faktor dominan yang memengaruhi prediksi ini adalah {factor_desc}. {agg_text}"
        )


llm_service = LLMExplanationService()