import numpy as np
from collections import deque

# Konstanta World Football Elo
INITIAL_ELO = 1500.0
K_FACTOR = 32.0
HOME_ADVANTAGE_ELO = 80.0


def calculate_expected_score(rating_a: float, rating_b: float) -> float:
    """Menghitung ekspektasi kemenangan berbasis probabilitas logistik Elo."""
    return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))


def update_elo(home_elo: float, away_elo: float, result: str, goal_diff: int):
    """Memperbarui rating True Elo kedua tim dengan margin of victory multiplier."""
    exp_home = calculate_expected_score(home_elo + HOME_ADVANTAGE_ELO, away_elo)
    exp_away = 1.0 - exp_home

    if result == "Home Win":
        actual_home, actual_away = 1.0, 0.0
    elif result == "Draw":
        actual_home, actual_away = 0.5, 0.5
    else:
        actual_home, actual_away = 0.0, 1.0

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
    home_rolling_scored_5: float,
    home_rolling_conceded_5: float,
    away_rolling_scored_5: float,
    away_rolling_conceded_5: float,
    home_form_pts_5: float,
    away_form_pts_5: float,
    home_elo: float,
    away_elo: float,
    home_leg1_score: int = 0,
    away_leg1_score: int = 0
) -> np.ndarray:
    """
    Ekstraksi Fitur Tingkat Lanjut:
    Menggabungkan Momentum 5 Laga Terakhir + True Elo + Dinamika Knockout Leg.
    """
    elo_diff = (home_elo + (HOME_ADVANTAGE_ELO if match_leg == 1 else 0.0)) - away_elo
    form_diff = home_form_pts_5 - away_form_pts_5

    agg_diff = 0.0
    if match_leg == 2:
        agg_diff = float(home_leg1_score - away_leg1_score)

    features = [
        float(match_leg),
        float(home_rolling_scored_5),
        float(home_rolling_conceded_5),
        float(away_rolling_scored_5),
        float(away_rolling_conceded_5),
        float(form_diff),
        float(elo_diff),
        float(agg_diff)
    ]
    return np.array([features], dtype=np.float32)


# 8 Fitur Mutakhir Standar Analisis Sepak Bola Modern
FEATURE_COLUMN_NAMES = [
    "match_leg",
    "home_rolling_scored_5",
    "home_rolling_conceded_5",
    "away_rolling_scored_5",
    "away_rolling_conceded_5",
    "form_points_diff_5",
    "elo_difference",
    "aggregate_difference"
]