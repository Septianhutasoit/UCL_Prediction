package service

import (
	"github.com/champintel/api/internal/client"
	"github.com/champintel/api/internal/model"
)

type PredictionService struct {
	AIClient *client.AIClient
}

func NewPredictionService(aiClient *client.AIClient) *PredictionService {
	return &PredictionService{
		AIClient: aiClient,
	}
}

func (s *PredictionService) ProcessPrediction(req model.PredictionRequest) (*model.PredictionResponse, error) {
	// Di sini nanti bisa ditambahkan logika tambahan (misal: simpan riwayat ke database PostgreSQL)
	// Untuk sekarang, langsung teruskan ke AI Client (FastAPI)
	return s.AIClient.GetPrediction(req)
}