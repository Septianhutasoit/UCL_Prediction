package main

import (
	"bytes"
	"io"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()

	// 1. Konfigurasi CORS agar Next.js di port 3000 bisa mengakses API
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:3000"},
		AllowMethods:     []string{"GET", "POST", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	// Alamat FastAPI AI Service (Default: http://localhost:8000)
	aiServiceURL := os.Getenv("AI_SERVICE_URL")
	if aiServiceURL == "" {
		aiServiceURL = "http://localhost:8000"
	}

	v1 := router.Group("/api/v1")
	{
		// Endpoint Health Check
		v1.GET("/health", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"status": "ok", "service": "ChampIntel Go Gateway"})
		})

		// 1. Proxy Route untuk Prediksi Match
		v1.POST("/predict", func(c *gin.Context) {
			proxyToFastAPI(c, aiServiceURL+"/predict")
		})

		// 2. Proxy Route untuk Simulasi What-if Scenario
		v1.POST("/simulate", func(c *gin.Context) {
			scenario := c.Query("scenario")
			targetURL := aiServiceURL + "/simulate"
			if scenario != "" {
				targetURL += "?scenario=" + scenario
			}
			proxyToFastAPI(c, targetURL)
		})

		// 3. [BARU] Proxy Route untuk Interactive AI Agent Query (Multi-Turn Chat)
		v1.POST("/agent/query", func(c *gin.Context) {
			proxyToFastAPI(c, aiServiceURL+"/agent/query")
		})
	}

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("🚀 ChampIntel Go Gateway berjalan di http://localhost:%s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatalf("Gagal menjalankan server: %v", err)
	}
}

// Helper function untuk meneruskan request ke FastAPI secara aman
func proxyToFastAPI(c *gin.Context, targetURL string) {
	body, err := io.ReadAll(c.Request.Body)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Gagal membaca body request"})
		return
	}

	client := &http.Client{Timeout: 15 * time.Second}
	req, err := http.NewRequest(http.MethodPost, targetURL, bytes.NewBuffer(body))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal membuat request ke AI Service"})
		return
	}

	req.Header.Set("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": "Gagal terhubung ke AI Service (FastAPI)"})
		return
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal membaca response dari AI Service"})
		return
	}

	c.Data(resp.StatusCode, "application/json", respBody)
}