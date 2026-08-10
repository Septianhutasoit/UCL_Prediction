'use client';

import React, { useState } from 'react';
import { fetchPrediction } from '@/lib/api';
import { PredictionResponse } from '@/lib/types';
import Image from 'next/image';

const teamLogoMap: { [key: string]: string } = {
  'Real Madrid': '/team/realmadrid.png',
  'Bayern Munich': '/team/bayern.png',
  'Arsenal': '/team/arsenal.png',
  'Manchester City': '/team/city.png',
  'Chelsea': '/team/chelsea.png',
  'Liverpool': '/team/liverpool.png',
  'Juventus': '/team/juve.png',
  'Paris Saint-Germain': '/team/psg.png',
  'Ajax': '/team/ajax.png',
};

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
    <div className="max-w-6xl mx-auto space-y-8">

      {/* Header Banner */}
      <div className="relative bg-gradient-to-r from-blue-900/40 via-indigo-950/40 to-slate-900 border border-slate-800 p-8 rounded-3xl overflow-hidden shadow-2xl flex items-center justify-between">
        <div className="relative z-10 space-y-2">
          <div className="inline-flex items-center space-x-2 bg-blue-500/10 border border-blue-500/20 px-3 py-1 rounded-full text-blue-400 text-xs font-semibold">
            <span>⚽ UEFA Champions League AI Engine</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">Match Intelligence & Prediction</h1>
          <p className="text-slate-400 text-sm max-w-xl">
            Analisis taktik mendalam dan probabilitas hasil laga fase gugur ditenagai oleh Machine Learning XGBoost.
          </p>
        </div>
        <div className="hidden md:block relative w-24 h-24 opacity-80">
          <Image src="/ucllogo.png" alt="UCL Logo" fill className="object-contain drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]" />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Form Konfigurasi */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl lg:col-span-1">
          <h2 className="text-base font-semibold mb-4 text-slate-200">Konfigurasi Pertandingan</h2>
          <form onSubmit={handlePredict} className="space-y-4">

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Tim Kandang (Home)</label>
              <div className="relative">
                <input
                  type="text"
                  value={homeTeam}
                  onChange={(e) => setHomeTeam(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
                  required
                />
                {teamLogoMap[homeTeam] && (
                  <div className="absolute left-3 top-2.5 w-5 h-5 relative">
                    <Image src={teamLogoMap[homeTeam]} alt={homeTeam} fill className="object-contain" />
                  </div>
                )}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Tim Tandang (Away)</label>
              <div className="relative">
                <input
                  type="text"
                  value={awayTeam}
                  onChange={(e) => setAwayTeam(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
                  required
                />
                {teamLogoMap[awayTeam] && (
                  <div className="absolute left-3 top-2.5 w-5 h-5 relative">
                    <Image src={teamLogoMap[awayTeam]} alt={awayTeam} fill className="object-contain" />
                  </div>
                )}
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">Babak / Leg</label>
              <select
                value={matchLeg}
                onChange={(e) => setMatchLeg(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                <option value={1}>Leg 1 (Single Match)</option>
                <option value={2}>Leg 2 (Knockout Aggregate)</option>
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
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-xl transition-all shadow-lg shadow-blue-600/20 disabled:opacity-50 mt-4 cursor-pointer"
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
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-6">
                <div>
                  <h3 className="text-xs font-semibold text-slate-400 mb-4 uppercase tracking-wider">Probabilitas Hasil Laga</h3>
                  <div className="grid grid-cols-3 gap-4 text-center">
                    <div className="bg-slate-950 border border-slate-800/60 p-4 rounded-xl flex flex-col items-center justify-center">
                      {teamLogoMap[homeTeam] && (
                        <div className="w-8 h-8 relative mb-2">
                          <Image src={teamLogoMap[homeTeam]} alt={homeTeam} fill className="object-contain" />
                        </div>
                      )}
                      <div className="text-2xl font-bold text-blue-400">{(result.home_win_prob * 100).toFixed(1)}%</div>
                      <div className="text-xs text-slate-400 mt-1">{homeTeam} Menang</div>
                    </div>

                    <div className="bg-slate-950 border border-slate-800/60 p-4 rounded-xl flex flex-col items-center justify-center">
                      <div className="text-2xl font-bold text-amber-400">{(result.draw_prob * 100).toFixed(1)}%</div>
                      <div className="text-xs text-slate-400 mt-1">Seri (Draw)</div>
                    </div>

                    <div className="bg-slate-950 border border-slate-800/60 p-4 rounded-xl flex flex-col items-center justify-center">
                      {teamLogoMap[awayTeam] && (
                        <div className="w-8 h-8 relative mb-2">
                          <Image src={teamLogoMap[awayTeam]} alt={awayTeam} fill className="object-contain" />
                        </div>
                      )}
                      <div className="text-2xl font-bold text-indigo-400">{(result.away_win_prob * 100).toFixed(1)}%</div>
                      <div className="text-xs text-slate-400 mt-1">{awayTeam} Menang</div>
                    </div>
                  </div>
                </div>

                {/* Peluang Kelolosan (Jika Leg 2) */}
                {result.home_qualification_prob !== null && result.home_qualification_prob !== undefined && (
                  <div className="pt-6 border-t border-slate-800">
                    <h3 className="text-xs font-semibold text-slate-400 mb-4 uppercase tracking-wider">Peluang Lolos ke Babak Berikutnya</h3>
                    <div className="grid grid-cols-2 gap-4 text-center">
                      <div className="bg-blue-950/20 border border-blue-900/40 p-4 rounded-xl">
                        <div className="text-xl font-bold text-blue-300">{(result.home_qualification_prob * 100).toFixed(1)}%</div>
                        <div className="text-xs text-blue-400/80 mt-1">{homeTeam} Lolos</div>
                      </div>
                      <div className="bg-indigo-950/20 border border-indigo-900/40 p-4 rounded-xl">
                        <div className="text-xl font-bold text-indigo-300">{(result.away_qualification_prob! * 100).toFixed(1)}%</div>
                        <div className="text-xs text-indigo-400/80 mt-1">{awayTeam} Lolos</div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Analisis AI */}
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl">
                <h3 className="text-xs font-semibold text-slate-400 mb-3 uppercase tracking-wider">Analisis Taktikal AI</h3>
                <p className="text-slate-300 text-sm leading-relaxed bg-slate-950 p-4 rounded-xl border border-slate-800/60">
                  {result.ai_analysis}
                </p>
              </div>
            </>
          ) : (
            <div className="bg-slate-900/50 border border-slate-800/60 border-dashed rounded-2xl h-full flex flex-col items-center justify-center p-12 text-center text-slate-500">
              <span className="text-4xl mb-2">⚽</span>
              <p className="text-sm">Silakan pilih klub, konfigurasi leg, lalu klik &quot;Jalankan Prediksi&quot;.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}