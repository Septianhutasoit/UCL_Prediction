import os
import sqlite3
import pandas as pd

def main():
    # Path ke database SQLite dan output CSV
    db_path = os.path.join("..", "datasets", "raw", "database.sqlite")
    output_csv = os.path.join("..", "datasets", "raw", "matches.csv")

    if not os.path.exists(db_path):
        print(f"❌ Error: Database {db_path} tidak ditemukan di folder raw!")
        return

    print("Menghubungkan ke database SQLite...")
    conn = sqlite3.connect(db_path)

    print("Mengekstrak tabel Match dan Team dari database...")
    # Ambil data pertandingan mentah dan tabel nama tim
    match_df = pd.read_sql("SELECT season, stage, date, home_team_api_id, away_team_api_id, home_team_goal, away_team_goal FROM Match", conn)
    team_df = pd.read_sql("SELECT team_api_id, team_long_name FROM Team", conn)
    conn.close()

    print("Mengonversi ID tim menjadi Nama Klub...")
    # Map ID tim ke nama panjang tim
    team_map = dict(zip(team_df['team_api_id'], team_df['team_long_name']))
    match_df['home_team'] = match_df['home_team_api_id'].map(team_map)
    match_df['away_team'] = match_df['away_team_api_id'].map(team_map)

    # Buat kolom skor dan hasil pertandingan (result)
    match_df['score'] = match_df['home_team_goal'].astype(str) + "–" + match_df['away_team_goal'].astype(str)
    
    def get_result(row):
        if row['home_team_goal'] > row['away_team_goal']:
            return "Home Win"
        elif row['home_team_goal'] < row['away_team_goal']:
            return "Away Win"
        else:
            return "Draw"

    match_df['result'] = match_df.apply(get_result, axis=1)

    # Bentuk dataframe final yang bersih
    final_df = pd.DataFrame({
        'date': match_df['date'],
        'season': match_df['season'],
        'stage': match_df['stage'],
        'home_team': match_df['home_team'],
        'away_team': match_df['away_team'],
        'score': match_df['score'],
        'home_goals': match_df['home_team_goal'],
        'away_goals': match_df['away_team_goal'],
        'result': match_df['result']
    })

    # Hapus baris yang datanya kosong / tidak lengkap
    final_df = final_df.dropna(subset=['home_team', 'away_team', 'result'])

    print(f"✨ Berhasil mengekstrak {len(final_df)} data pertandingan bersih!")

    # Simpan menimpa matches.csv yang lama
    final_df.to_csv(output_csv, index=False)
    print(f"📁 File CSV baru berhasil dibuat di: {output_csv}")

if __name__ == "__main__":
    main()