package main

import (
	"os"

	"github.com/champintel/api/internal/client"
	"github.com/champintel/api/internal/handler"
	"github.com/champintel/api/internal/service"
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	// Ambil URL FastAPI dari environment variable, atau default ke http://localhost:8000
	aiServiceURL := os.Getenv("AI_SERVICE_URL")
	if aiServiceURL == "" {
		aiServiceURL = "http://localhost:8000" // Sesuaikan dengan port uvicorn FastAPI kamu
	}

	// Inisialisasi arsitektur (Dependency Injection)
	aiClient := client.NewAIClient(aiServiceURL)
	predService := service.NewPredictionService(aiClient)
	predHandler := handler.NewPredictionHandler(predService)

	// --- ROUTES ---
	r.GET("/api/v1/health", handler.HealthCheck)
	r.POST("/api/v1/predict", predHandler.PredictMatch)

	// Jalankan server Go di port 8080
	r.Run(":8080")
}