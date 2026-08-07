import os
import json
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def main():
    # 1. Tentukan path dataset
    csv_path = os.path.join("..", "datasets", "sample", "sample_matches.csv")
    model_dir = os.path.join("..", "models")
    
    if not os.path.exists(csv_path):
        csv_path = os.path.join("..", "datasets", "raw", "matches.csv")

    print(f"Memuat dataset dari: {csv_path}")
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()

    print("📋 Kolom fitur yang ditemukan:", df.columns.tolist())

    # 2. Pisahkan Fitur (X) dan Target (y)
    X = df.iloc[:, :-1]  # Semua kolom kecuali terakhir
    y = df.iloc[:, -1].astype(int)  # Kolom terakhir (target)

    # 3. Saring X HANYA untuk kolom angka (membuang nama tim seperti home_team, away_team)
    X = X.select_dtypes(include=['number'])
    print("📊 Fitur numerik yang digunakan:", X.columns.tolist())

    # 4. Split data menjadi Training dan Testing (Wajib dilakukan SEBELUM model.fit)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Melatih model XGBoost...")
    model = xgb.XGBClassifier(
        objective="multi:softprob",
        num_class=3,
        max_depth=3,
        learning_rate=0.1,
        n_estimators=50,
        random_state=42
    )

    # 5. Latih model
    model.fit(X_train, y_train)

    # 6. Evaluasi model
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"🎉 Model berhasil dilatih! Akurasi pada data uji: {acc * 100:.2f}%")

    # 7. Simpan model dan daftar kolom fitur
    model_path = os.path.join(model_dir, "xgboost_ucl.json")
    meta_path = os.path.join(model_dir, "feature_columns.json")
    
    model.save_model(model_path)
    with open(meta_path, "w") as f:
        json.dump(X.columns.tolist(), f)

    print(f"📁 Model tersimpan di: {model_path}")
    print(f"📁 Metadata fitur tersimpan di: {meta_path}")

if __name__ == "__main__":
    main()