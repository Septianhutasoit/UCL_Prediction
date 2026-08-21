package handler

import (
	"net/http"

	"github.com/champintel/api/internal/model"
	"github.com/champintel/api/internal/service"
	"github.com/gin-gonic/gin"
)

type PredictionHandler struct {
	Service *service.PredictionService
}

func NewPredictionHandler(service *service.PredictionService) *PredictionHandler {
	return &PredictionHandler{
		Service: service,
	}
}

func (h *PredictionHandler) PredictMatch(c *gin.Context) {
	var req model.PredictionRequest

	// 1. Validasi dan bind JSON request dari user/frontend
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 2. Panggil service untuk memproses prediksi
	res, err := h.Service.ProcessPrediction(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{
			"error": "Gagal mendapatkan prediksi dari AI Service: " + err.Error(),
		})
		return
	}

	// 3. Kembalikan hasil ke frontend
	c.JSON(http.StatusOK, res)
}

func (h *PredictionHandler) SimulateMatch(c *gin.Context) {
    var req model.PredictionRequest
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }
    scenario := c.DefaultQuery("scenario", "neutral_venue")
    
    // Panggil client ke FastAPI
    res, err := h.Service.AIClient.SimulateMatch(req, scenario)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }
    c.JSON(http.StatusOK, res)
}

func (h *PredictionHandler) GetHistory(c *gin.Context) {
	if h.Service.Repo == nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Database belum terhubung"})
		return
	}

	list, err := h.Service.Repo.GetAllPredictions()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Gagal mengambil riwayat: " + err.Error()})
		return
	}

	c.JSON(http.StatusOK, list)
}