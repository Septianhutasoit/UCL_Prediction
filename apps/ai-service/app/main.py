from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.predict import router as predict_router

app = FastAPI(
    title="Uefa Champions League AI Service",
    description="AI Enginer for UCL Match Prediction & Analysis",
    version="1.0.0",
)

# Configurasi CORS agar bisa diakses oleh backend Go (Prabo Go)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "service": "ai-service"}

app.include_router(predict_router)