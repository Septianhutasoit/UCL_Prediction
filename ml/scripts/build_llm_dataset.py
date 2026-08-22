import os
import sys
import json
import random

# Hubungkan root dan apps/ai-service ke sys.path secara aman
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
AI_SERVICE_DIR = os.path.join(ROOT_DIR, "apps", "ai-service")

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
if AI_SERVICE_DIR not in sys.path:
    sys.path.append(AI_SERVICE_DIR)

from app.services.predictor import predictor

# Roster Resmi UCL yang 100% Cocok dengan lib/teams.ts dan team_stats.json
UCL_ROSTER = [
    "Real Madrid", "Barcelona", "Bayern Munich", "Manchester City",
    "Arsenal", "Liverpool", "Paris Saint-Germain", "Inter", "Juventus",
    "Borussia Dortmund", "Atletico Madrid", "Bayer Leverkusen", "Aston Villa",
    "Benfica", "Sporting CP", "Atalanta", "Milan", "PSV"
]


def generate_tactical_narrative(home, away, h_prob, d_prob, a_prob, top_factor, leg, h_leg1, a_leg1):
    """Memilih template narasi taktik yang 100% JUJUR terhadap angka probabilitas."""
    factor_text = top_factor.get("feature", "performa tim") if isinstance(top_factor, dict) else str(top_factor)

    # 1. Kasus: Tuan Rumah (Home) Diunggulkan
    if h_prob >= a_prob + 0.08:
        templates = [
            f"Berdasarkan pemodelan probabilitas XGBoost, {home} diunggulkan menang ({h_prob*100:.1f}%) atas {away} ({a_prob*100:.1f}%). Faktor dominan terletak pada {factor_text}, yang memberikan keunggulan intensitas serangan dan kontrol tempo di kandang.",
            f"{home} memegang kendali probabilitas sebesar {h_prob*100:.1f}%. Didukung oleh {factor_text}, tuan rumah diproyeksikan mampu mendikte permainan dan menekan lini pertahanan {away} sejak menit awal."
        ]
    # 2. Kasus: Tim Tamu (Away) Lebih Diunggulkan
    elif a_prob >= h_prob + 0.08:
        templates = [
            f"Meskipun bermain tandang, {away} justru lebih diunggulkan dengan probabilitas kemenangan {a_prob*100:.1f}% berbanding {h_prob*100:.1f}% milik {home}. Keunggulan {factor_text} menjadi faktor pembeda yang membuat tim tamu difavoritkan membawa poin penuh.",
            f"Model memproyeksikan {away} berpeluang besar mencuri kemenangan di kandang {home} ({a_prob*100:.1f}% vs {h_prob*100:.1f}%). Soliditas taktik dan efektivitas {factor_text} diperkirakan mampu meredam tekanan suporter tuan rumah."
        ]
    # 3. Kasus: Laga Ketat / Berimbang / Seri
    else:
        templates = [
            f"Pertandingan diproyeksikan berjalan sangat berimbang dengan peluang seri {d_prob*100:.1f}% (Home {h_prob*100:.1f}% vs Away {a_prob*100:.1f}%). Pengaruh {factor_text} menjadikan duel lini tengah berlangsung alot dengan margin kesalahan yang sangat tipis.",
            f"Kedua tim memiliki kekuatan taktis yang setara ({home} {h_prob*100:.1f}% vs {away} {a_prob*100:.1f}%). Faktor penentu laga ini bergantung pada {factor_text} dalam memanfaatkan transisi peluang krusial."
        ]

    narrative = random.choice(templates)
    if leg == 2:
        narrative += f" Dengan agregat Leg 1 ({h_leg1}-{a_leg1}), manajemen risiko dan tempo akan sangat krusial hingga menit akhir."

    return narrative


def build_datasets():
    output_dir = os.path.join(ROOT_DIR, "ml", "datasets", "llm")
    os.makedirs(output_dir, exist_ok=True)

    dataset_samples = []
    print("🚀 Menjalankan Bulk Dataset Generator via predict_raw()...")

    # Uji coba seluruh kombinasi tim
    for home in UCL_ROSTER:
        for away in UCL_ROSTER:
            if home == away:
                continue

            for leg in [1, 2]:
                h_leg1 = random.randint(0, 3) if leg == 2 else 0
                a_leg1 = random.randint(0, 3) if leg == 2 else 0

                # Panggil predict_raw (XGBoost + SHAP murni, cepat & hemat)
                res = predictor.predict_raw({
                    "home_team": home,
                    "away_team": away,
                    "match_leg": leg,
                    "home_leg1_score": h_leg1,
                    "away_leg1_score": a_leg1
                })

                h_prob = res["home_win_prob"]
                d_prob = res["draw_prob"]
                a_prob = res["away_win_prob"]
                top_factor = res["top_factors"][0] if res.get("top_factors") else {"feature": "selisih True Elo"}

                user_prompt = (
                    f"Pertandingan: {home} vs {away}. Leg: {leg}. "
                    f"Probabilitas: Home Win {h_prob*100:.1f}%, Draw {d_prob*100:.1f}%, Away Win {a_prob*100:.1f}%. "
                    f"Faktor Kunci: {top_factor.get('feature', 'Elo Rating')}."
                )
                if leg == 2:
                    user_prompt += f" Agregat Leg 1: {h_leg1}-{a_leg1}."

                assistant_response = generate_tactical_narrative(
                    home, away, h_prob, d_prob, a_prob, top_factor, leg, h_leg1, a_leg1
                )

                sample = {
                    "messages": [
                        {
                            "role": "system",
                            "content": "Kamu adalah analis taktik sepak bola UEFA Champions League yang objektif, presisi terhadap data probabilitas, dan berbasis analisis numerik."
                        },
                        {"role": "user", "content": user_prompt},
                        {"role": "assistant", "content": assistant_response}
                    ]
                }
                dataset_samples.append(sample)

    random.seed(42)
    random.shuffle(dataset_samples)

    split_point = int(len(dataset_samples) * 0.85)
    train_data = dataset_samples[:split_point]
    val_data = dataset_samples[split_point:]

    train_path = os.path.join(output_dir, "train.jsonl")
    val_path = os.path.join(output_dir, "validation.jsonl")

    with open(train_path, "w", encoding="utf-8") as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    with open(val_path, "w", encoding="utf-8") as f:
        for item in val_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"🎉 SUKSES! Dihasilkan {len(train_data)} data train.jsonl & {len(val_data)} data validation.jsonl.")


if __name__ == "__main__":
    build_datasets()