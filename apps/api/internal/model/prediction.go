package model

type PredictionResponse struct {
	HomeWinProb           float64 `json:"home_win_prob"`
	DrawProb              float64 `json:"draw_prob"`
	AwayWinProb           float64 `json:"away_win_prob"`
	HomeQualificationProb float64 `json:"home_qualification_prob,omitempty"` // Khusus Leg 2
	AwayQualificationProb float64 `json:"away_qualification_prob,omitempty"` // Khusus Leg 2
	AIAnalysis            string  `json:"ai_analysis"`
}