'use client';

import React, { useState } from 'react';
import { fetchPrediction } from '@/lib/api';
import { PredictionResponse } from '@/lib/types';

export default function Home() {
  const [homeTeam, setHomeTeam] = useState('Real Madrid');
  const [awayTeam, setAwayTeam] = useState('Bayern Munich');
  const [matchLeg, setMatchLeg] = useState(2);
  const [homeLeg1, setHomeLeg1] = useState(1);
  const [awayLeg1, setAwayLeg1] = useState(2);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState('');

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const data = await fetchPrediction({
        home_team: homeTeam,
        away_team: awayTeam,
        match_leg: Number(matchLeg),
        home_leg1_score: matchLeg === 2 ? Number(homeLeg1) : null,
        away_leg1_score: matchLeg === 2 ? Number(awayLeg1) : null,
        home_win_rate: 0.75,
        away_win_rate: 0.65,
        elo_difference: 45.0,
      });
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Terjadi kesalahan sistem.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">UCL Match Predictor</h1>
        <p className="text-slate-400 mt-1">
          Prediksi probabilitas hasil pertandingan dan peluang kelolosan fase gugur menggunakan XGBoost & AI.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form Input */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl lg:col-span-1">
          <h2 className="text-lg font-semibold mb-4 text-slate-200">Konfigurasi Laga</h2>
          <form onSubmit={handlePredict} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Tim Kandang (Home)</label>
              <input
                type="text"
                value={homeTeam}
                onChange={(e) => setHomeTeam(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Tim Tandang (Away)</label>
              <input
                type="text"
                value={awayTeam}
                onChange={(e) => setAwayTeam(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Babak / Leg</label>
              <select
                value={matchLeg}
                onChange={(e) => setMatchLeg(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                <option value={1}>Leg 1 (Single / Leg Pertama)</option>
                <option value={2}>Leg 2 (Penentuan / Agregat)</option>
              </select>
            </div>

            {matchLeg === 2 && (
              <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-800">
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Gol Leg 1 ({homeTeam})</label>
                  <input
                    type="number"
                    value={homeLeg1}
                    onChange={(e) => setHomeLeg1(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-white focus:outline-none"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-400 mb-1">Gol Leg 1 ({awayTeam})</label>
                  <input
                    type="number"
                    value={awayLeg1}
                    onChange={(e) => setAwayLeg1(Number(e.target.value))}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-white focus:outline-none"
                  />
                </div>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-xl transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 mt-4"
            >
              {loading ? 'Menganalisis Data AI...' : 'Jalankan Prediksi 🚀'}
            </button>
          </form>

          {error && <p className="text-red-400 text-xs mt-4">{error}</p>}
        </div>

        {/* Hasil Prediksi */}
        <div className="lg:col-span-2 space-y-6">
          {result ? (
            <>
              {/* Kartu Probabilitas */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
                <h3 className="text-sm font-semibold text-slate-400 mb-4 uppercase tracking-wider">Probabilitas Hasil Laga</h3>
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div className="bg-slate-950 border border-slate-800/60 p-4 rounded-xl">
                    <div className="text-2xl font-bold text-blue-400">{(result.home_win_prob * 100).toFixed(1)}%</div>
                    <div className="text-xs text-slate-400 mt-1">{homeTeam} Menang</div>
                  </div>
                  <div className="bg-slate-950 border border-slate-800/60 p-4 rounded-xl">
                    <div className="text-2xl font-bold text-amber-400">{(result.draw_prob * 100).toFixed(1)}%</div>
                    <div className="text-xs text-slate-400 mt-1">Seri (Draw)</div>
                  </div>
                  <div className="bg-slate-950 border border-slate-800/60 p-4 rounded-xl">
                    <div className="text-2xl font-bold text-indigo-400">{(result.away_win_prob * 100).toFixed(1)}%</div>
                    <div className="text-xs text-slate-400 mt-1">{awayTeam} Menang</div>
                  </div>
                </div>

                {/* Peluang Kelolosan (Jika Leg 2) */}
                {result.home_qualification_prob !== null && result.home_qualification_prob !== undefined && (
                  <div className="mt-6 pt-6 border-t border-slate-800">
                    <h3 className="text-sm font-semibold text-slate-400 mb-4 uppercase tracking-wider">Peluang Lolos ke Babak Berikutnya</h3>
                    <div className="grid grid-cols-2 gap-4 text-center">
                      <div className="bg-blue-950/30 border border-blue-900/40 p-4 rounded-xl">
                        <div className="text-xl font-bold text-blue-300">{(result.home_qualification_prob * 100).toFixed(1)}%</div>
                        <div className="text-xs text-blue-400/80 mt-1">{homeTeam} Lolos</div>
                      </div>
                      <div className="bg-indigo-950/30 border border-indigo-900/40 p-4 rounded-xl">
                        <div className="text-xl font-bold text-indigo-300">{(result.away_qualification_prob! * 100).toFixed(1)}%</div>
                        <div className="text-xs text-indigo-400/80 mt-1">{awayTeam} Lolos</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Analisis AI */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
                <h3 className="text-sm font-semibold text-slate-400 mb-3 uppercase tracking-wider">Analisis Taktikal AI</h3>
                <p className="text-slate-300 text-sm leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800/60">
                  {result.ai_analysis}
                </p>
              </div>
            </>
          ) : (
            <div className="bg-slate-900/50 border border-slate-800/60 border-dashed rounded-2xl h-full flex flex-col items-center justify-center p-12 text-center text-slate-500">
              <span className="text-4xl mb-2">⚽</span>
              <p className="text-sm">Silakan masukkan data laga dan klik &quot;Jalankan Prediksi&quot; untuk melihat hasil analisis AI.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}