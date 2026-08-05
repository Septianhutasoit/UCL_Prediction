package main

import (
	"github.com/gin-gonic/gin"
	"github.com/champintel/api/internal/handler"
)

func main() {
	r := gin.Default()

	// Route Health Check
	r.GET("/api/v1/health", handler.HealthCheck)

	// Jalankan server di port 8080
	r.Run(":8080")
}