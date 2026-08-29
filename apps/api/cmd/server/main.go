package main

import (
	"bytes"
	"encoding/json"
	"io"
	"log"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

type HistoryItem struct {
	ID                    string   `json:"id"`
	HomeTeam              string   `json:"home_team"`
	AwayTeam              string   `json:"away_team"`
	MatchLeg              int      `json:"match_leg"`
	HomeLeg1Score         int      `json:"home_leg1_score"`
	AwayLeg1Score         int      `json:"away_leg1_score"`
	HomeWinProb           float64  `json:"home_win_prob"`
	DrawProb              float64  `json:"draw_prob"`
	AwayWinProb           float64  `json:"away_win_prob"`
	HomeQualificationProb *float64 `json:"home_qualification_prob,omitempty"`
	AwayQualificationProb *float64 `json:"away_qualification_prob,omitempty"`
	AIAnalysis            string   `json:"ai_analysis"`
	CreatedAt             string   `json:"created_at"`
}

var (
	historyList  = []HistoryItem{}
	historyMutex sync.RWMutex
)

func main() {
	router := gin.Default()

	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:3000"},
		AllowMethods:     []string{"GET", "POST", "OPTIONS"},
		AllowHeaders:     []string{"Origin", "Content-Type", "Accept"},
		ExposeHeaders:    []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           12 * time.Hour,
	}))

	aiServiceURL := os.Getenv("AI_SERVICE_URL")
	if aiServiceURL == "" {
		aiServiceURL = "http://localhost:8000"
	}

	v1 := router.Group("/api/v1")
	{
		v1.GET("/health", func(c *gin.Context) {
			c.JSON(http.StatusOK, gin.H{"status": "ok", "service": "ChampIntel Go Gateway"})
		})

		// 1. Proxy Route Prediksi Match (sekaligus simpan riwayat)
		v1.POST("/predict", func(c *gin.Context) {
			proxyAndSavePredict(c, aiServiceURL+"/predict")
		})

		// 2. Proxy Route Simulasi What-if Scenario
		v1.POST("/simulate", func(c *gin.Context) {
			scenario := c.Query("scenario")
			targetURL := aiServiceURL + "/simulate"
			if scenario != "" {
				targetURL += "?scenario=" + scenario
			}
			proxyToFastAPI(c, targetURL)
		})

		// 3. Proxy Route Interactive AI Agent
		v1.POST("/agent/query", func(c *gin.Context) {
			proxyToFastAPI(c, aiServiceURL+"/agent/query")
		})

		// 4. [BARU] Endpoint GET & POST History
		v1.GET("/history", func(c *gin.Context) {
			historyMutex.RLock()
			defer historyMutex.RUnlock()
			c.JSON(http.StatusOK, historyList)
		})

		v1.POST("/history", func(c *gin.Context) {
			var item HistoryItem
			if err := c.ShouldBindJSON(&item); err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
				return
			}
			if item.CreatedAt == "" {
				item.CreatedAt = time.Now().Format(time.RFC3339)
			}
			historyMutex.Lock()
			historyList = append([]HistoryItem{item}, historyList...)
			historyMutex.Unlock()
			c.JSON(http.StatusCreated, item)
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

func proxyAndSavePredict(c *gin.Context, targetURL string) {
	body, err := io.ReadAll(c.Request.Body)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Gagal membaca body request"})
		return
	}

	client := &http.Client{Timeout: 15 * time.Second}
	req, err := http.NewRequest(http.MethodPost, targetURL, bytes.NewBuffer(body))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal membuat request"})
		return
	}

	req.Header.Set("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": "Gagal terhubung ke AI Service"})
		return
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal membaca response"})
		return
	}

	// Simpan hasil ke history jika berhasil
	if resp.StatusCode == http.StatusOK {
		var reqMap map[string]interface{}
		var respMap map[string]interface{}
		_ = json.Unmarshal(body, &reqMap)
		_ = json.Unmarshal(respBody, &respMap)

		item := HistoryItem{
			ID:          time.Now().Format("20060102150405"),
			HomeTeam:    reqMap["home_team"].(string),
			AwayTeam:    reqMap["away_team"].(string),
			MatchLeg:    int(reqMap["match_leg"].(float64)),
			HomeWinProb: respMap["home_win_prob"].(float64),
			DrawProb:    respMap["draw_prob"].(float64),
			AwayWinProb: respMap["away_win_prob"].(float64),
			AIAnalysis:  respMap["ai_analysis"].(string),
			CreatedAt:   time.Now().Format("02 Jan 2006, 15:04"),
		}
		historyMutex.Lock()
		historyList = append([]HistoryItem{item}, historyList...)
		historyMutex.Unlock()
	}

	c.Data(resp.StatusCode, "application/json", respBody)
}

func proxyToFastAPI(c *gin.Context, targetURL string) {
	body, err := io.ReadAll(c.Request.Body)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Gagal membaca body request"})
		return
	}

	client := &http.Client{Timeout: 15 * time.Second}
	req, err := http.NewRequest(http.MethodPost, targetURL, bytes.NewBuffer(body))
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal membuat request"})
		return
	}

	req.Header.Set("Content-Type", "application/json")
	resp, err := client.Do(req)
	if err != nil {
		c.JSON(http.StatusBadGateway, gin.H{"error": "Gagal terhubung ke AI Service"})
		return
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal membaca response"})
		return
	}

	c.Data(resp.StatusCode, "application/json", respBody)
}