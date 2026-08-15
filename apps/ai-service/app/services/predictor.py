import os
import json
import numpy as np
import xgboost as xgb

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
                
                with open(self.meta_path, "r") as f:
                    self.feature_columns = json.load(f)
                    
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

        # Ambil statistik historis asli dari team_stats.json (jika ada, jika tidak pakai nilai rata-rata liga)
        h_stats = self.team_stats.get(home_team, {"avg_scored": 1.5, "avg_conceded": 1.0, "win_rate": 0.5})
        a_stats = self.team_stats.get(away_team, {"avg_scored": 1.3, "avg_conceded": 1.2, "win_rate": 0.4})

        # Susun input sesuai urutan fitur saat training
        # feature_columns = ["match_leg", "home_avg_scored", "home_avg_conceded", "away_avg_scored", "away_avg_conceded", "elo_difference"]
        input_data = [
            float(data.get("match_leg", 1)),
            float(h_stats["avg_scored"]),
            float(h_stats["avg_conceded"]),
            float(a_stats["avg_scored"]),
            float(a_stats["avg_conceded"]),
            float(data.get("elo_difference", 0.0))
        ]

        X = np.array([input_data])
        probs = self.model.predict_proba(X)[0]
        
        away_win_prob = float(probs[0])
        draw_prob = float(probs[1])
        home_win_prob = float(probs[2])

        analysis = (
            f"Analisis XGBoost (Data Historis Asli): "
            f"Berdasarkan rekam jejak performa gol ({home_team} mencetak rata-rata {h_stats['avg_scored']} gol/laga vs {away_team} {a_stats['avg_scored']} gol/laga), "
            f"peluang kemenangan kandang diperkirakan {home_win_prob*100:.1f}%, Seri {draw_prob*100:.1f}%, dan kemenangan tandang {away_win_prob*100:.1f}%."
        )

        home_qual = None
        away_qual = None
        if data.get("match_leg") == 2:
            h_agg = data.get("home_leg1_score", 0) or 0
            a_agg = data.get("away_leg1_score", 0) or 0
            
            # Kalkulasi kelolosan berbasis probabilitas menang + agregat leg 1
            agg_diff = h_agg - a_agg
            home_qual = round(0.5 + (home_win_prob - away_win_prob) * 0.3 + (agg_diff * 0.1), 2)
            home_qual = max(0.05, min(0.95, home_qual))
            away_qual = round(1.0 - home_qual, 2)
            
            analysis += f" Mengingat skor Leg 1 ({home_team} {h_agg} - {a_agg} {away_team}), agregat sementara memengaruhi peluang kelolosan menjadi {home_qual*100:.1f}% untuk {home_team} dan {away_qual*100:.1f}% untuk {away_team}."

        return {
            "home_win_prob": round(home_win_prob, 2),
            "draw_prob": round(draw_prob, 2),
            "away_win_prob": round(away_win_prob, 2),
            "home_qualification_prob": home_qual,
            "away_qualification_prob": away_qual,
            "ai_analysis": analysis
        }
    
    def simulate_scenario(self, data: dict, scenario_type: str):
        # jalankan prediksi normal sebagai baseline
        base_result = self.predict(data)

        # salin data untuk modifikasi
        mod_data = data.copy()
        scenario_title = ""

        if scenario_type == "neutral_venue":
            scenario_title = "Skenario: Tempat Netral (Tanpa Keunggulan Kandang)"
            # Simulasi: Kurangi sedikit kekuatan kandang
            home_team = mod_data.get("home_team")
            if home_team in self.team_stats:
                # Buat tiruan data dengan avg_scored kandang diturunkan sedikit
                pass
                
        elif scenario_type == "aggressive_tactic":
            scenario_title = "Skenario: Taktik Super Agresif (All-Out Attack)"
            # Simulasi taktik menyerang total
            pass

        # 3. Jalankan prediksi ulang dengan data skenario
        scenario_result = self.predict(mod_data)
        
        # Hitung selisih probabilitas
        diff = round(scenario_result["home_win_prob"] - base_result["home_win_prob"], 2)
        
        return {
            "scenario_name": scenario_title,
            "baseline": base_result,
            "scenario_result": scenario_result,
            "probability_difference": diff,
            "explanation": f"Berdasarkan {scenario_title}, probabilitas kemenangan tim kandang berubah sebesar {diff*100:+.1f}% dibanding kondisi normal."
        }

predictor = UCLPredictor()