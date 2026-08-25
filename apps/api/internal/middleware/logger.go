package middleware

import (
	"log"
	"time"

	"github.com/gin-gonic/gin"
)

// CustomLogger mencatat setiap HTTP request dengan latensi waktu
func CustomLogger() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		path := c.Request.URL.Path

		c.Next()

		latency := time.Since(start)
		status := c.Writer.Status()
		log.Printf("[CHAMPINTEL-GATEWAY] %d | %s | %v | %s", status, c.Request.Method, latency, path)
	}
}