import os
import json
import numpy as np
import xgboost as xgb

from app.services.shap_explainer import UCLShapExplainer
from app.services.llm_service import llm_service

def find_project_root(current_dir, target_folder="ml"):
    while current_dir != os.path.dirname(current_dir):
        if os.path.exists(os.path.join(current_dir, target_folder)):
            return current_dir
        current_dir = os.path.dirname(current_dir)
    return None

class UCLPredictor:
    def __init__(self):
        current_file_dir = os.path.dirname(os.path.abspath(__file__))
        root_dir = find_project_root(current_file_dir, target_folder="ml")
        
        if root_dir:
            self.model_path = os.path.join(root_dir, "ml", "models", "xgboost_ucl.json")
            self.meta_path = os.path.join(root_dir, "ml", "models", "feature_columns.json")
            self.stats_path = os.path.join(root_dir, "ml", "models", "team_stats.json")
        else:
            self.model_path = os.path.abspath("ml/models/xgboost_ucl.json")
            self.meta_path = os.path.abspath("ml/models/feature_columns.json")
            self.stats_path = os.path.abspath("ml/models/team_stats.json")

        self.model = None
        self.feature_columns = []
        self.team_stats = {}
        self.load_model()

    def load_model(self):
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.meta_path):
                self.model = xgb.XGBClassifier()
                self.model.load_model(self.model_path)
                
                # 1. Baca metadata fitur terlebih dahulu
                with open(self.meta_path, "r") as f:
                    self.feature_columns = json.load(f)
                    
                # 2. Baru inisialisasi SHAP Explainer dengan feature_columns yang sudah terisi
                self.shap_explainer = UCLShapExplainer(self.model, self.feature_columns)
                    
                if os.path.exists(self.stats_path):
                    with open(self.stats_path, "r") as f:
                        self.team_stats = json.load(f)
                        
                print(f">>> Model XGBoost & Profil Tim ({len(self.team_stats)} klub) BERHASIL dimuat ke FastAPI! <<<")
            else:
                print(">>> Peringatan: File model XGBoost belum ditemukan! <<<")
        except Exception as e:
            print(f"🔥 Gagal memuat model: {str(e)}")

    def predict(self, data: dict):
        if self.model is None:
            return {
                "home_win_prob": 0.50,
                "draw_prob": 0.25,
                "away_win_prob": 0.25,
                "ai_analysis": "Model XGBoost belum dimuat."
            }

        home_team = data.get("home_team")
        away_team = data.get("away_team")

        # Ambil statistik historis asli dari team_stats.json
        h_stats = self.team_stats.get(home_team, {"avg_scored": 1.5, "avg_conceded": 1.0, "win_rate": 0.5})
        a_stats = self.team_stats.get(away_team, {"avg_scored": 1.3, "avg_conceded": 1.2, "win_rate": 0.4})

        # Menggabungkan win_rate dan selisih gol bersih untuk merepresentasikan kekuatan tim
        h_power = (h_stats["win_rate"] * 2.0) + (h_stats["avg_scored"] - h_stats["avg_conceded"])
        a_power = (a_stats["win_rate"] * 2.0) + (a_stats["avg_scored"] - a_stats["avg_conceded"])
        
        # Skala perbedaan kekuatan (dibuat menyerupai selisih Elo rating)
        calculated_elo_diff = round((h_power - a_power) * 100, 2)
        # -------------------------------------------------------------------

        # Susun input sesuai urutan fitur saat training
        input_data = [
            float(data.get("match_leg", 1)),
            float(h_stats["avg_scored"]),
            float(h_stats["avg_conceded"]),
            float(a_stats["avg_scored"]),
            float(a_stats["avg_conceded"]),
            float(calculated_elo_diff) # <--- Sekarang menggunakan nilai dinamis yang valid!
        ]

        X = np.array([input_data])
        top_factors = self.shap_explainer.explain(X)
        probs = self.model.predict_proba(X)[0]
        
        away_win_prob = float(probs[0])
        draw_prob = float(probs[1])
        home_win_prob = float(probs[2])

        home_qual = None
        away_qual = None
        if data.get("match_leg") == 2:
            h_agg = data.get("home_leg1_score", 0) or 0
            a_agg = data.get("away_leg1_score", 0) or 0
            
            agg_diff = h_agg - a_agg
            home_qual = round(0.5 + (home_win_prob - away_win_prob) * 0.3 + (agg_diff * 0.1), 2)
            home_qual = max(0.05, min(0.95, home_qual))
            away_qual = round(1.0 - home_qual, 2)

        # Buat konteks agregat untuk LLM
        agg_text = ""
        if data.get("match_leg") == 2:
            h_agg = data.get("home_leg1_score", 0) or 0
            a_agg = data.get("away_leg1_score", 0) or 0
            agg_text = f"Skor Leg 1: {home_team} {h_agg} - {a_agg} {away_team}. Peluang lolos: {home_team} ({home_qual*100:.1f}%) vs {away_team} ({away_qual*100:.1f}%)."

        # Panggil Qwen LLM untuk merangkum analisis secara natural
        probs_dict = {
            "home_win_prob": home_win_prob,
            "draw_prob": draw_prob,
            "away_win_prob": away_win_prob
        }
        analysis = llm_service.generate_explanation(home_team, away_team, probs_dict, top_factors, data.get("match_leg", 1), agg_text)
        return {
            "home_win_prob": round(home_win_prob, 2),
            "draw_prob": round(draw_prob, 2),
            "away_win_prob": round(away_win_prob, 2),
            "home_qualification_prob": home_qual,
            "away_qualification_prob": away_qual,
            "ai_analysis": analysis,
            "top_factors": top_factors
        }
    
    def simulate_scenario(self, data: dict, scenario_type: str):
        # 1. Dapatkan prediksi normal (baseline)
        base_result = self.predict(data)
        base_h = base_result["home_win_prob"]
        
        h_prob = base_h
        d_prob = base_result["draw_prob"]
        a_prob = base_result["away_win_prob"]
        
        scenario_title = ""
        explanation = ""
        
        # 2. Kalkulasi taktis berdasarkan skenario
        if scenario_type == "neutral_venue":
            scenario_title = "Skenario: Tempat Netral (Tanpa Keunggulan Kandang)"
            h_prob = max(0.05, h_prob - 0.09)
            d_prob = d_prob + 0.04
            a_prob = a_prob + 0.05
            explanation = f"Bermain di tempat netral menghilangkan keuntungan psikologis kandang bagi {data.get('home_team')}."
            
        elif scenario_type == "aggressive_tactic":
            scenario_title = "Skenario: Taktik Super Agresif (All-Out Attack)"
            h_prob = min(0.95, h_prob + 0.12)
            d_prob = max(0.05, d_prob - 0.08)
            a_prob = max(0.05, a_prob - 0.04)
            explanation = f"Menerapkan strategi menyerang total meningkatkan intensitas gol {data.get('home_team')}."

        # Normalisasi total probabilitas agar pas 100% (1.0)
        total = h_prob + d_prob + a_prob
        h_prob = round(h_prob / total, 2)
        d_prob = round(d_prob / total, 2)
        a_prob = round(1.0 - h_prob - d_prob, 2)

        scenario_result = {
            "home_win_prob": h_prob,
            "draw_prob": d_prob,
            "away_win_prob": a_prob,
            "home_qualification_prob": base_result.get("home_qualification_prob"),
            "away_qualification_prob": base_result.get("away_qualification_prob"),
            "ai_analysis": explanation
        }

        diff = round(h_prob - base_h, 2)
        
        # --- CETAK KE TERMINAL FASTAPI UNTUK CEK ---
        print(f"🔍 DEBUG -> Base Win: {base_h} | Scenario Win: {h_prob} | Diff: {diff}")

        return {
            "scenario_name": scenario_title,
            "baseline": base_result,
            "scenario_result": scenario_result,
            "probability_difference": diff,
            "explanation": explanation
        }
    

predictor = UCLPredictor()