import os
import sys
import json
import random

# Kunci Seed di Baris Paling Awal agar 100% Reproducible
random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
AI_SERVICE_DIR = os.path.join(ROOT_DIR, "apps", "ai-service")

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)
if AI_SERVICE_DIR not in sys.path:
    sys.path.append(AI_SERVICE_DIR)

from app.services.predictor import predictor

# 36 Roster Lengkap Peserta UEFA Champions League (Format Baru)
UCL_ROSTER_36 = [
    "Real Madrid", "Manchester City", "Bayern Munich", "Barcelona", "Arsenal",
    "Liverpool", "Paris Saint-Germain", "Inter", "Bayer Leverkusen", "Atletico Madrid",
    "Borussia Dortmund", "Juventus", "Atalanta", "Benfica", "Sporting CP",
    "Milan", "PSV", "Aston Villa", "Monaco", "RB Leipzig", "Feyenoord",
    "Celtic", "Club Brugge", "Shakhtar Donetsk", "Lille", "Girona",
    "Stuttgart", "Bologna", "Sparta Praha", "Brest", "Salzburg",
    "Young Boys", "Crvena Zvezda", "Slovan Bratislava", "Dinamo Zagreb", "Sturm Graz"
]

# 10 Ragam Sudut Pandang Taktikal Sepak Bola Modern
TACTICAL_VARIATIONS = [
    # 1. High-Pressing & Half-Space Overload
    "Mengandalkan intensitas high-pressing di lini depan, {favored} berpeluang besar mendikte tempo dan memaksa {underdog} melakukan kesalahan fatal saat build-up dari lini belakang. Pemanfaatan area half-space akan menjadi jalur utama membongkar compact defense.",
    
    # 2. Rest-Defense & Counter-Attack Transition
    "Meskipun menghadapi struktur pertahanan rapat, efektivitas rest-defense {favored} menjadi fondasi penting untuk mencegah serangan balik kilat {underdog}. Kecepatan transisi dari bertahan ke menyerang diprediksi menjadi kunci lahirnya gol penentu.",
    
    # 3. Midfield Dominance & Second Balls
    "Pertarungan krusial akan terjadi di poros lini sentral. {favored} memiliki keunggulan dalam memenangkan perebutan bola kedua (second balls), yang memaksa {underdog} bermain lebih pasif dan terisolasi di sepertiga akhir lapangan.",
    
    # 4. Low-Block & Set-Piece Threat
    "{underdog} diproyeksikan akan menerapkan medium-to-low block berlapis untuk merapatkan ruang antar lini. Peluang terbaik mereka untuk membalikkan prediksi adalah melalui skema bola mati (set-piece) dan serangan langsung (direct balls).",
    
    # 5. Overload to Isolate Wingers
    "Strategi overload di salah satu sisi sayap akan digunakan untuk menciptakan situasi satu lawan satu (1v1 isolation) bagi penyerang sayap {favored}, menguji kedisiplinan bek sayap {underdog} sepanjang 90 menit."
]


def generate_rich_tactical_text(home, away, h_prob, d_prob, a_prob, top_factor, leg, h_leg1, a_leg1):
    """Menghasilkan teks taktis kaya dengan bahasa analis sepak bola profesional."""
    factor_name = top_factor.get("feature", "True Elo Difference") if isinstance(top_factor, dict) else str(top_factor)
    
    h_pct = f"{h_prob*100:.1f}%"
    d_pct = f"{d_prob*100:.1f}%"
    a_pct = f"{a_prob*100:.1f}%"

    if h_prob >= a_prob + 0.08:
        favored, underdog = home, away
        intro = f"Berdasarkan pemodelan probabilitas XGBoost untuk Leg ke-{leg}, {home} diunggulkan menang dengan probabilitas {h_pct}, berbanding {a_pct} untuk {away} dan potensi seri {d_pct}."
        reason = f"Keunggulan {home} didorong kuat oleh faktor {factor_name}. "
        tactic = random.choice(TACTICAL_VARIATIONS[:3]).format(favored=home, underdog=away)
    elif a_prob >= h_prob + 0.08:
        favored, underdog = away, home
        intro = f"Meskipun berstatus tim tamu pada Leg ke-{leg}, {away} justru memegang kendali probabilitas kemenangan sebesar {a_pct}, sementara {home} mencatatkan {h_pct} dan seri {d_pct}."
        reason = f"Efektivitas {factor_name} menjadi pembeda utama dalam duel ini. "
        tactic = random.choice(TACTICAL_VARIATIONS[1:4]).format(favored=away, underdog=home)
    else:
        intro = f"Pertandingan Leg ke-{leg} antara {home} dan {away} diproyeksikan berlangsung sangat ketat dan berimbang (Home {h_pct}, Seri {d_pct}, Away {a_pct})."
        reason = f"Margin kekuatan kedua tim sangat tipis dengan pengaruh utama pada {factor_name}. "
        tactic = random.choice(TACTICAL_VARIATIONS[2:]).format(favored=home, underdog=away)

    agg_text = f" Membawa agregat Leg 1 ({h_leg1}-{a_leg1}), manajemen risiko akan menjadi penentu kelolosan hingga menit akhir." if leg == 2 else ""

    return f"{intro} {reason}{tactic}{agg_text}"


def build_massive_datasets():
    output_dir = os.path.join(ROOT_DIR, "ml", "datasets", "llm")
    os.makedirs(output_dir, exist_ok=True)

    dataset_samples = []
    print("🚀 Menghasilkan 1.200+ Dataset Taktis UCL Komprehensif...")

    # Buat kombinasi pertandingan kaya dari 36 tim
    for i in range(len(UCL_ROSTER_36)):
        for j in range(i + 1, len(UCL_ROSTER_36)):
            home, away = UCL_ROSTER_36[i], UCL_ROSTER_36[j]

            # Uji kedua sisi (Home vs Away & Away vs Home)
            for h_team, a_team in [(home, away), (away, home)]:
                # Uji Leg 1 dan berbagai skenario skor Leg 2
                scenarios = [(1, 0, 0), (2, 0, 0), (2, 1, 0), (2, 0, 2), (2, 2, 1), (2, 3, 0)]
                
                for leg, h_leg1, a_leg1 in scenarios:
                    res = predictor.predict_raw({
                        "home_team": h_team,
                        "away_team": a_team,
                        "match_leg": leg,
                        "home_leg1_score": h_leg1,
                        "away_leg1_score": a_leg1
                    })

                    h_prob = res["home_win_prob"]
                    d_prob = res["draw_prob"]
                    a_prob = res["away_win_prob"]
                    top_factor = res["top_factors"][0] if res.get("top_factors") else {"feature": "True Elo"}

                    user_prompt = (
                        f"Pertandingan: {h_team} vs {a_team}. Leg: {leg}. "
                        f"Probabilitas: Home Win {h_prob*100:.1f}%, Draw {d_prob*100:.1f}%, Away Win {a_prob*100:.1f}%. "
                        f"Faktor Kunci: {top_factor.get('feature', 'Elo Rating')}."
                    )
                    if leg == 2:
                        user_prompt += f" Agregat Leg 1: {h_leg1}-{a_leg1}."

                    assistant_text = generate_rich_tactical_text(
                        h_team, a_team, h_prob, d_prob, a_prob, top_factor, leg, h_leg1, a_leg1
                    )

                    sample = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "Kamu adalah analis taktik sepak bola UEFA Champions League yang objektif, presisi terhadap data probabilitas XGBoost, dan berbasis analisis numerik."
                            },
                            {"role": "user", "content": user_prompt},
                            {"role": "assistant", "content": assistant_text}
                        ]
                    }
                    dataset_samples.append(sample)

    # 3-Way Split Resmi: 70% Train, 15% Validation, 15% Holdout Test
    random.shuffle(dataset_samples)
    total = len(dataset_samples)
    train_end = int(total * 0.70)
    val_end = int(total * 0.85)

    train_data = dataset_samples[:train_end]
    val_data = dataset_samples[train_end:val_end]
    test_data = dataset_samples[val_end:]

    train_path = os.path.join(output_dir, "train.jsonl")
    val_path = os.path.join(output_dir, "validation.jsonl")
    test_path = os.path.join(output_dir, "test.jsonl")

    for path, data in [(train_path, train_data), (val_path, val_data), (test_path, test_data)]:
        with open(path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"🎉 SUKSES BESAR! Berhasil membuat {total:,} total dataset taktis!")
    print(f"📦 Train Set       : {len(train_data):,} data (70%)")
    print(f"📊 Validation Set  : {len(val_data):,} data (15%)")
    print(f"🧪 Holdout Test Set: {len(test_data):,} data (15%)")


if __name__ == "__main__":
    build_massive_datasets()