import os
import sys
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
            if root_dir not in sys.path:
                sys.path.append(root_dir)
        else:
            self.model_path = os.path.abspath("ml/models/xgboost_ucl.json")
            self.meta_path = os.path.abspath("ml/models/feature_columns.json")
            self.stats_path = os.path.abspath("ml/models/team_stats.json")

        from ml.features.feature_builder import extract_match_features, INITIAL_ELO
        self.extract_match_features = extract_match_features
        self.INITIAL_ELO = INITIAL_ELO

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

                self.shap_explainer = UCLShapExplainer(self.model, self.feature_columns)

                if os.path.exists(self.stats_path):
                    with open(self.stats_path, "r") as f:
                        self.team_stats = json.load(f)

                print(f">>> Model XGBoost & Profil Tim ({len(self.team_stats)} klub) BERHASIL dimuat ke FastAPI! <<<")
            else:
                print(">>> Peringatan: File model XGBoost belum ditemukan! <<<")
        except Exception as e:
            print(f"🔥 Gagal memuat model: {str(e)}")

    def _predict_core(self, data: dict):
        """Fungsi inti: Menghitung probabilitas XGBoost dan SHAP tanpa memanggil LLM."""
        if self.model is None:
            return None

        home_team = data.get("home_team")
        away_team = data.get("away_team")
        match_leg = data.get("match_leg", 1)
        home_leg1_score = data.get("home_leg1_score", 0) or 0
        away_leg1_score = data.get("away_leg1_score", 0) or 0

        h_stats = self.team_stats.get(
            home_team, {"elo_rating": self.INITIAL_ELO, "avg_scored": 1.5, "avg_conceded": 1.0}
        )
        a_stats = self.team_stats.get(
            away_team, {"elo_rating": self.INITIAL_ELO, "avg_scored": 1.3, "avg_conceded": 1.2}
        )
        h_elo = h_stats.get("elo_rating", self.INITIAL_ELO)
        a_elo = a_stats.get("elo_rating", self.INITIAL_ELO)

        X = self.extract_match_features(
            match_leg=match_leg,
            home_rolling_scored=h_stats["avg_scored"],
            home_rolling_conceded=h_stats["avg_conceded"],
            away_rolling_scored=a_stats["avg_scored"],
            away_rolling_conceded=a_stats["avg_conceded"],
            home_elo=h_elo,
            away_elo=a_elo,
            home_leg1_score=home_leg1_score,
            away_leg1_score=away_leg1_score,
        )

        top_factors = self.shap_explainer.explain(X)
        probs = self.model.predict_proba(X)[0]

        away_win_prob = float(probs[0])
        draw_prob = float(probs[1])
        home_win_prob = float(probs[2])

        home_qual = None
        away_qual = None
        if match_leg == 2:
            agg_diff = home_leg1_score - away_leg1_score
            home_qual = round(0.5 + (home_win_prob - away_win_prob) * 0.3 + (agg_diff * 0.1), 2)
            home_qual = max(0.05, min(0.95, home_qual))
            away_qual = round(1.0 - home_qual, 2)

        return {
            "home_team": home_team,
            "away_team": away_team,
            "match_leg": match_leg,
            "home_leg1_score": home_leg1_score,
            "away_leg1_score": away_leg1_score,
            "home_win_prob": round(home_win_prob, 2),
            "draw_prob": round(draw_prob, 2),
            "away_win_prob": round(away_win_prob, 2),
            "home_qualification_prob": home_qual,
            "away_qualification_prob": away_qual,
            "top_factors": top_factors,
            "home_elo": round(h_elo, 1),
            "away_elo": round(a_elo, 1),
        }

    def predict_raw(self, data: dict):
        """Method cepat untuk generator dataset (XGBoost + SHAP saja, SKIP LLM)."""
        core = self._predict_core(data)
        if core is None:
            return {"home_win_prob": 0.50, "draw_prob": 0.25, "away_win_prob": 0.25, "top_factors": []}
        return core

    def predict(self, data: dict):
        """Method publik untuk API: Menggabungkan hasil core + Narasi LLM."""
        core = self._predict_core(data)
        if core is None:
            return {
                "home_win_prob": 0.50,
                "draw_prob": 0.25,
                "away_win_prob": 0.25,
                "ai_analysis": "Model XGBoost belum dimuat."
            }

        # Format konteks agregat
        agg_text = ""
        if core["match_leg"] == 2:
            agg_text = (
                f"Skor Leg 1: {core['home_team']} {core['home_leg1_score']} - {core['away_leg1_score']} {core['away_team']}. "
                f"Peluang lolos: {core['home_team']} ({core['home_qualification_prob']*100:.1f}%) vs {core['away_team']} ({core['away_qualification_prob']*100:.1f}%)."
            )

        probs_dict = {
            "home_win_prob": core["home_win_prob"],
            "draw_prob": core["draw_prob"],
            "away_win_prob": core["away_win_prob"]
        }

        # Panggil LLM Qwen untuk merangkum teks
        analysis = llm_service.generate_explanation(
            core["home_team"], core["away_team"], probs_dict, core["top_factors"], core["match_leg"], agg_text
        )

        result = dict(core)
        result["ai_analysis"] = analysis
        return result

    def simulate_scenario(self, data: dict, scenario_type: str):
        # 1. PERBAIKAN BUG 1: Gunakan predict_raw() (SKIP pemanggilan LLM agar 10x lebih cepat)
        base_result = self.predict_raw(data)
        base_h = base_result["home_win_prob"]

        h_prob = base_h
        d_prob = base_result["draw_prob"]
        a_prob = base_result["away_win_prob"]
        match_leg = data.get("match_leg", 1)
        h_leg1 = data.get("home_leg1_score", 0) or 0
        a_leg1 = data.get("away_leg1_score", 0) or 0

        scenario_title = ""
        explanation = ""

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

        # Normalisasi probabilitas agar totalnya tetap 1.0 (100%)
        total = h_prob + d_prob + a_prob
        h_prob = round(h_prob / total, 2)
        d_prob = round(d_prob / total, 2)
        a_prob = round(1.0 - h_prob - d_prob, 2)

        # 2. PERBAIKAN BUG 2: Hitung ulang peluang kelolosan (Qualification Prob) jika Leg 2
        scenario_home_qual = None
        scenario_away_qual = None
        if match_leg == 2:
            agg_diff = h_leg1 - a_leg1
            scenario_home_qual = round(0.5 + (h_prob - a_prob) * 0.3 + (agg_diff * 0.1), 2)
            scenario_home_qual = max(0.05, min(0.95, scenario_home_qual))
            scenario_away_qual = round(1.0 - scenario_home_qual, 2)

        scenario_result = {
            "home_win_prob": h_prob,
            "draw_prob": d_prob,
            "away_win_prob": a_prob,
            "home_qualification_prob": scenario_home_qual,
            "away_qualification_prob": scenario_away_qual,
            "ai_analysis": explanation
        }

        diff = round(h_prob - base_h, 2)

        return {
            "scenario_name": scenario_title,
            "baseline": base_result,
            "scenario_result": scenario_result,
            "probability_difference": diff,
            "explanation": explanation
        }


predictor = UCLPredictor()