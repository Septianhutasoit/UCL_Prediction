package model

type ShapFactor struct {
	Feature string  `json:"feature"`
	Value   float64 `json:"value"`
	Impact  string  `json:"impact"`
}

type PredictionResponse struct {
	HomeWinProb           float64      `json:"home_win_prob"`
	DrawProb              float64      `json:"draw_prob"`
	AwayWinProb           float64      `json:"away_win_prob"`
	HomeQualificationProb *float64     `json:"home_qualification_prob,omitempty"` // <--- Harus pakai pointer *float64
	AwayQualificationProb *float64     `json:"away_qualification_prob,omitempty"` // <--- Harus pakai pointer *float64
	AIAnalysis            string       `json:"ai_analysis"`
	TopFactors            []ShapFactor `json:"top_factors"`
}