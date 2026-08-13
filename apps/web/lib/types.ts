export interface PredictionRequest {
    home_team: string;
    away_team: string;
    match_leg: number;
    home_leg1_score?: number | null;
    away_leg1_score?: number | null;
}

export interface PredictionResponse {
    home_win_prob: number;
    draw_prob: number;
    away_win_prob: number;
    home_qualification_prob?: number | null;
    away_qualification_prob?: number | null;
    ai_analysis: string;
}