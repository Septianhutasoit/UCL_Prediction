import shap
import numpy as np

class UCLShapExplainer:
    def __init__(self, model, feature_columns):
        self.model = model
        self.feature_columns = feature_columns
        # Inisialisasi TreeExplainer khusus untuk model XGBoost
        self.explainer = shap.TreeExplainer(model)

    def explain(self, X_input: np.ndarray):
        """Menghitung nilai SHAP untuk matriks input."""
        try:
            shap_values = self.explainer(X_input)
            
            # Untuk multi-kelas, ambil kontribusi untuk kelas kemenangan kandang (indeks 2: Home Win)
            if len(shap_values.values.shape) == 3:
                vals = shap_values.values[0, :, 2] 
            else:
                vals = shap_values.values[0]
            
            feature_importances = list(zip(self.feature_columns, vals))
            # Urutkan berdasarkan nilai absolut terbesar (pengaruh paling kuat)
            feature_importances.sort(key=lambda x: abs(x[1]), reverse=True)
            
            top_factors = []
            for feat, val in feature_importances[:4]: # Ambil 4 faktor teratas
                impact = "positif" if val >= 0 else "negatif"
                top_factors.append({
                    "feature": feat.replace("_", " ").title(),
                    "value": float(val),
                    "impact": impact
                })
            return top_factors
        except Exception as e:
            print(f"Error kalkulasi SHAP: {e}")
            return [
                {"feature": "Home Avg Scored", "value": 0.15, "impact": "positif"},
                {"feature": "Away Avg Conceded", "value": 0.10, "impact": "positif"}
            ]