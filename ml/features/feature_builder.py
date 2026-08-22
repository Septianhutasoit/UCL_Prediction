import numpy as np

# Konstanta World Football Elo
INITIAL_ELO = 1500.0
K_FACTOR = 30.0
HOME_ADVANTAGE_ELO = 80.0  # Bobot keuntungan kandang dalam poin Elo


def calculate_expected_score(rating_a: float, rating_b: float) -> float:
    """Menghitung ekspektasi kemenangan berbasis probabilitas logistik Elo."""
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))


def update_elo(home_elo: float, away_elo: float, result: str, goal_diff: int):
    """
    Memperbarui rating Elo kedua tim setelah pertandingan dengan penyesuaian selisih gol.
    """
    # Ekspektasi dengan memperhitungkan faktor kandang
    exp_home = calculate_expected_score(home_elo + HOME_ADVANTAGE_ELO, away_elo)
    exp_away = 1.0 - exp_home

    # Hasil aktual
    if result == "Home Win":
        actual_home, actual_away = 1.0, 0.0
    elif result == "Draw":
        actual_home, actual_away = 0.5, 0.5
    else:
        actual_home, actual_away = 0.0, 1.0

    # Pengali margin kemenangan
    margin_mult = 1.0
    if abs(goal_diff) == 2:
        margin_mult = 1.5
    elif abs(goal_diff) >= 3:
        margin_mult = 1.75 + (abs(goal_diff) - 3) / 8.0

    delta_home = K_FACTOR * margin_mult * (actual_home - exp_home)
    delta_away = K_FACTOR * margin_mult * (actual_away - exp_away)

    return home_elo + delta_home, away_elo + delta_away


def extract_match_features(
    match_leg: int,
    home_rolling_scored: float,
    home_rolling_conceded: float,
    away_rolling_scored: float,
    away_rolling_conceded: float,
    home_elo: float,
    away_elo: float,
    home_leg1_score: int = 0,
    away_leg1_score: int = 0
) -> np.ndarray:
    """
    Membangun array fitur terpadu yang 100% IDENTIK antara training dan runtime FastAPI.
    """
    elo_diff = (home_elo + (HOME_ADVANTAGE_ELO if match_leg == 1 else 0.0)) - away_elo

    # Hitung agregat beban jika Leg 2
    agg_diff = 0.0
    if match_leg == 2:
        agg_diff = float(home_leg1_score - away_leg1_score)

    features = [
        float(match_leg),
        float(home_rolling_scored),
        float(home_rolling_conceded),
        float(away_rolling_scored),
        float(away_rolling_conceded),
        float(elo_diff),
        float(agg_diff)
    ]
    return np.array([features], dtype=np.float32)


FEATURE_COLUMN_NAMES = [
    "match_leg",
    "home_avg_scored",
    "home_avg_conceded",
    "away_avg_scored",
    "away_avg_conceded",
    "elo_difference",
    "aggregate_difference"
]