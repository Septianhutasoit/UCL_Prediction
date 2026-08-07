import os
import json
import numpy as np
import xgboost as xgb

class UCLPredictor:
    def __init__(self):
        base_dir = r"E:\Projects\UCLMADRID\ml\models"
        
        self.model_path = os.path.join(base_dir, "xgboost_ucl.json")
        self.meta_path = os.path.join(base_dir, "feature_columns.json")
        
        self.model = None
        self.feature_columns = []
        self.load_model()

    def load_model(self):
        try:
            print(f"Mencoba memuat model dari: {self.model_path}")
            if os.path.exists(self.model_path) and os.path.exists(self.meta_path):
                self.model = xgb.XGBClassifier()
                self.model.load_model(self.model_path)
                
                with open(self.meta_path, "r") as f:
                    self.feature_columns = json.load(f)
                print(">>> Model XGBoost asli BERHASIL dimuat ke FastAPI! <<<")
            else:
                print(">>> Peringatan: File model XGBoost TIDAK DITEMUKAN di path tersebut! <<<")
        except Exception as e:
            print(f"🔥 GAGAL TOTAL MEMUAT MODEL: {str(e)}")

    def predict(self, data: dict):
        if self.model is None:
            return {
                "home_win_prob": 0.50,
                "draw_prob": 0.25,
                "away_win_prob": 0.25,
                "ai_analysis": "Model XGBoost belum dimuat, menggunakan prediksi cadangan."
            }

        input_data = []
        for col in self.feature_columns:
            input_data.append(float(data.get(col, 0.0)))

        X = np.array([input_data])
        probs = self.model.predict_proba(X)[0]
        
        away_win_prob = float(probs[0])
        draw_prob = float(probs[1])
        home_win_prob = float(probs[2])

        analysis = (
            f"Analisis XGBoost (Model Asli): "
            f"Peluang kemenangan tim kandang {home_win_prob*100:.1f}%, "
            f"Seri {draw_prob*100:.1f}%, "
            f"Peluang kemenangan tim tandang {away_win_prob*100:.1f}%."
        )

        home_qual = None
        away_qual = None
        if data.get("match_leg") == 2:
            h_agg = data.get("home_aggregate_before", 0)
            a_agg = data.get("away_aggregate_before", 0)
            
            home_qual = round(0.5 + (home_win_prob - away_win_prob) * 0.4, 2)
            home_qual = max(0.0, min(1.0, home_qual))
            away_qual = round(1.0 - home_qual, 2)
            
            analysis += f" Berdasarkan agregat (Leg 1: {h_agg}-{a_agg}), peluang kelolosan diperkirakan {home_qual*100:.1f}% untuk tim kandang dan {away_qual*100:.1f}% untuk tim tandang."

        return {
            "home_win_prob": round(home_win_prob, 2),
            "draw_prob": round(draw_prob, 2),
            "away_win_prob": round(away_win_prob, 2),
            "home_qualification_prob": home_qual,
            "away_qualification_prob": away_qual,
            "ai_analysis": analysis
        }

predictor = UCLPredictor()