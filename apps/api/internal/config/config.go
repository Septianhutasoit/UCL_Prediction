package config

import (
	"os"
)

type Config struct {
	Port         string
	AIServiceURL string
}

func LoadConfig() *Config {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	aiURL := os.Getenv("AI_SERVICE_URL")
	if aiURL == "" {
		aiURL = "http://localhost:8000"
	}

	return &Config{
		Port:         port,
		AIServiceURL: aiURL,
	}
}