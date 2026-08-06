package model

type PredictionRequest struct {
	HomeTeam      string  `json:"home_team" binding:"required"`
	AwayTeam      string  `json:"away_team" binding:"required"`
	MatchLeg      int     `json:"match_leg" binding:"required"` // 1 atau 2
	HomeLeg1Score *int    `json:"home_leg1_score"`              // Boleh null jika leg 1
	AwayLeg1Score *int    `json:"away_leg1_score"`              // Boleh null jika leg 1
	HomeWinRate   float64 `json:"home_win_rate"`
	AwayWinRate   float64 `json:"away_win_rate"`
	HomeElo       float64 `json:"home_elo"`
	EloDifference float64 `json:"elo_difference"`
}