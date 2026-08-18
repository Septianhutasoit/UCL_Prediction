 import os

class Settings:
    PROJECT_NAME: str = "ChampIntel AI Service"
    VERSION: str = "1.0.0"
    MODEL_PATH: str = os.getenv("MODEL_PATH", "ml/models/xgboost_ucl.json")

settings = Settings()
