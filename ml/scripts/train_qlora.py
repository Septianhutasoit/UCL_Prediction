import os
import sys

def main():
    print("🧠 ChampIntel QLoRA Fine-Tuning CLI Guide:")
    print("=" * 50)
    print("1. Melatih Qwen 2.5 (1.5B) membutuhkan GPU NVIDIA (CUDA).")
    print("2. Untuk pengguna tanpa GPU lokal, jalankan via Google Colab T4 GPU:")
    print("   -> Buka ml/notebooks/03_qlora_finetuning.ipynb")
    print("3. Ekspor adapter otomatis tersimpan di: apps/ai-service/models/ucl_qwen_adapter")
    print("=" * 50)

if __name__ == "__main__":
    main()
