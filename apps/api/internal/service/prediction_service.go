package service

import (
	"github.com/champintel/api/internal/client"
	"github.com/champintel/api/internal/model"
	"github.com/champintel/api/internal/repository"
)

type PredictionService struct {
	AIClient *client.AIClient
	Repo     *repository.PredictionRepository
}

func NewPredictionService(aiClient *client.AIClient, repo *repository.PredictionRepository) *PredictionService {
	return &PredictionService{
		AIClient: aiClient,
		Repo:     repo,
	}
}

func (s *PredictionService) ProcessPrediction(req model.PredictionRequest) (*model.PredictionResponse, error) {
	// 1. Ambil hasil prediksi dari AI Service (FastAPI)
	res, err := s.AIClient.GetPrediction(req)
	if err != nil {
		return nil, err
	}

	// 2. Simpan secara permanen ke PostgreSQL (Supabase) secara background (async)
	if s.Repo != nil {
		go func() {
			_ = s.Repo.SavePrediction(req, res)
		}()
	}

	return res, nil
}