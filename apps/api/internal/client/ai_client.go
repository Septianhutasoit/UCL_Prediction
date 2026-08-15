package client

import (
	"bytes"
	"encoding/json"
	"errors"
	"net/http"
	"time"

	"github.com/champintel/api/internal/model"
)

type AIClient struct {
	BaseURL    string
	HttpClient *http.Client
}

// NewAIClient membuat instance baru untuk klien AI
func NewAIClient(baseURL string) *AIClient {
	return &AIClient{
		BaseURL: baseURL,
		HttpClient: &http.Client{
			Timeout: 15 * time.Second,
		},
	}
}

// GetPrediction mengirim data pertandingan ke FastAPI dan menerima hasil prediksi
func (c *AIClient) GetPrediction(req model.PredictionRequest) (*model.PredictionResponse, error) {
	// 1. Ubah struct Go menjadi JSON
	jsonBody, err := json.Marshal(req)
	if err != nil {
		return nil, err
	}

	// 2. Kirim HTTP POST request ke FastAPI (/predict)
	resp, err := c.HttpClient.Post(c.BaseURL+"/predict", "application/json", bytes.NewBuffer(jsonBody))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	// 3. Cek apakah status code dari FastAPI itu sukses (200 OK)
	if resp.StatusCode != http.StatusOK {
		return nil, errors.New("ai service returned non-200 status code")
	}

	// 4. Decode JSON response dari FastAPI ke struct PredictionResponse
	var result model.PredictionResponse
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return &result, nil
}

func (c *AIClient) SimulateMatch(req model.PredictionRequest, scenario string) (map[string]interface{}, error) {
	jsonBody, err := json.Marshal(req)
	if err != nil {
		return nil, err
	}

	url := c.BaseURL + "/simulate?scenario=" + scenario
	resp, err := c.HttpClient.Post(url, "application/json", bytes.NewBuffer(jsonBody))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var result map[string]interface{}
	if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
		return nil, err
	}

	return result, nil
}