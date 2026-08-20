package repository

import (
	"database/sql"

	"github.com/champintel/api/internal/model"
	_ "github.com/lib/pq"
)

type PredictionRepository struct {
	DB *sql.DB
}

func NewPredictionRepository(connStr string) (*PredictionRepository, error) {
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return nil, err
	}
	if err := db.Ping(); err != nil {
		return nil, err
	}
	return &PredictionRepository{DB: db}, nil
}

func (r *PredictionRepository) SavePrediction(req model.PredictionRequest, res *model.PredictionResponse) error {
	query := `
		INSERT INTO predictions (home_team, away_team, match_leg, home_win_prob, draw_prob, away_win_prob, home_qual_prob, away_qual_prob, ai_analysis)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
	`
	var hQual, aQual *float64 = res.HomeQualificationProb, res.AwayQualificationProb

	_, err := r.DB.Exec(query, 
		req.HomeTeam, req.AwayTeam, req.MatchLeg, 
		res.HomeWinProb, res.DrawProb, res.AwayWinProb, 
		hQual, aQual, res.AIAnalysis,
	)
	return err
}

func (r *PredictionRepository) GetAllPredictions() ([]map[string]interface{}, error) {
	rows, err := r.DB.Query("SELECT id, home_team, away_team, match_leg, home_win_prob, draw_prob, away_win_prob, ai_analysis, created_at FROM predictions ORDER BY id DESC LIMIT 50")
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var list []map[string]interface{}
	for rows.Next() {
		var id int
		var home, away, analysis string
		var leg int
		var hWin, dWin, aWin float64
		var createdAt string

		if err := rows.Scan(&id, &home, &away, &leg, &hWin, &dWin, &aWin, &analysis, &createdAt); err != nil {
			continue
		}

		item := map[string]interface{}{
			"id":        id,
			"home_team": home,
			"away_team": away,
			"match_leg": leg,
			"result": map[string]interface{}{
				"home_win_prob": hWin,
				"draw_prob":     dWin,
				"away_win_prob": aWin,
				"ai_analysis":   analysis,
			},
			"date": createdAt,
		}
		list = append(list, item)
	}
	return list, nil
}