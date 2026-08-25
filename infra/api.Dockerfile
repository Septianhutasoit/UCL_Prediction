FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY apps/api/go.mod apps/api/go.sum* ./
RUN go mod download
COPY apps/api/ .
RUN CGO_ENABLED=0 GOOS=linux go build -o server cmd/server/main.go

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app/server .
EXPOSE 8080
CMD ["./server"]