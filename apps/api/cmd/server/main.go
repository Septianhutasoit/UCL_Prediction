package main

import (
	"log"
	"os"

	"github.com/champintel/api/internal/client"
	"github.com/champintel/api/internal/handler"
	"github.com/champintel/api/internal/middleware"
	"github.com/champintel/api/internal/repository"
	"github.com/champintel/api/internal/service"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	// Load file .env di folder api jika ada
	_ = godotenv.Load()

	r := gin.Default()
	r.Use(middleware.CORSMiddleware())

	// Koneksi ke Database PostgreSQL Supabase
	dbURL := os.Getenv("DB_URL")
	var predRepo *repository.PredictionRepository
	if dbURL != "" {
		var err error
		predRepo, err = repository.NewPredictionRepository(dbURL)
		if err != nil {
			log.Printf("⚠️ Warning: Gagal terhubung ke Database Supabase: %v", err)
		} else {
			log.Println(">>> 🚀 Berhasil terhubung ke Database PostgreSQL (Supabase)! <<<")
		}
	} else {
		log.Println("⚠️ Warning: DB_URL tidak ditemukan di file .env")
	}

	aiServiceURL := os.Getenv("AI_SERVICE_URL")
	if aiServiceURL == "" {
		aiServiceURL = "http://localhost:8000"
	}

	// Inisialisasi Arsitektur
	aiClient := client.NewAIClient(aiServiceURL)
	predService := service.NewPredictionService(aiClient, predRepo)
	predHandler := handler.NewPredictionHandler(predService)

	// --- ROUTES ---
	r.GET("/api/v1/health", handler.HealthCheck)
	r.POST("/api/v1/predict", predHandler.PredictMatch)
	r.POST("/api/v1/simulate", predHandler.SimulateMatch)

	// Jalankan server Go di port 8080
	r.Run(":8080")
}