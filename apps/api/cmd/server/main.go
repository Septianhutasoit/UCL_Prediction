package main

import (
	"os"

	"github.com/champintel/api/internal/client"
	"github.com/champintel/api/internal/handler"
	"github.com/champintel/api/internal/middleware"
	"github.com/champintel/api/internal/service"
	"github.com/gin-gonic/gin"
)

func main() {
	r := gin.Default()

	r.Use(middleware.CORSMiddleware())

	aiServiceURL := os.Getenv("AI_SERVICE_URL")
	if aiServiceURL == "" {
		aiServiceURL = "http://localhost:8000"
	}

	aiClient := client.NewAIClient(aiServiceURL)
	predService := service.NewPredictionService(aiClient)
	predHandler := handler.NewPredictionHandler(predService)

	r.GET("/api/v1/health", handler.HealthCheck)
	r.POST("/api/v1/predict", predHandler.PredictMatch)
	r.POST("/api/v1/simulate", predHandler.SimulateMatch)

	r.Run(":8080")
}