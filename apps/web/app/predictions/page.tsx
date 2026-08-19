'use client';

import React, { useState } from 'react';
import MatchCard from '@/components/MatchCard';
import PredictionResult from '@/components/PredictionResult';
import { fetchPrediction } from '@/lib/api';
import { PredictionResponse } from '@/lib/types';
import { Sparkles, Trophy } from 'lucide-react';

const marqueeFixtures = [
    { home: 'Real Madrid', away: 'Manchester City', stage: 'Quarter-Final Leg 2', homeLogo: '/team/realmadrid.png', awayLogo: '/team/city.png' },
    { home: 'Bayern Munich', away: 'Arsenal', stage: 'Quarter-Final Leg 2', homeLogo: '/team/bayern.png', awayLogo: '/team/arsenal.png' },
    { home: 'Barcelona', away: 'Paris Saint-Germain', stage: 'Quarter-Final Leg 2', homeLogo: '/team/barca.png', awayLogo: '/team/psg.png' },
    { home: 'Inter Milan', away: 'Atlético Madrid', stage: 'Round of 16 Leg 2', homeLogo: '/team/inter.png', awayLogo: '/team/atm.png' },
    { home: 'Juventus', away: 'Benfica', stage: 'League Phase', homeLogo: '/team/juve.png', awayLogo: '/team/benfica.png' },
    { home: 'Liverpool', away: 'Borussia Dortmund', stage: 'League Phase', homeLogo: '/team/liverpool.png', awayLogo: '/team/dortmund.png' },
];

export default function LiveAnalysisPage() {
    const [selectedMatch, setSelectedMatch] = useState<any | null>(null);
    const [homeLeg1, setHomeLeg1] = useState(1);
    const [awayLeg1, setAwayLeg1] = useState(1);
    const [matchLeg, setMatchLeg] = useState(2);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<PredictionResponse | null>(null);

    const handleSelectMatch = (match: any) => {
        setSelectedMatch(match);
        setResult(null);
        setHomeLeg1(1);
        setAwayLeg1(1);
    };

    const handleAnalyze = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!selectedMatch) return;

        setLoading(true);
        setResult(null);

        try {
            const data = await fetchPrediction({
                home_team: selectedMatch.home,
                away_team: selectedMatch.away,
                match_leg: Number(matchLeg),
                home_leg1_score: matchLeg === 2 ? Number(homeLeg1) : null,
                away_leg1_score: matchLeg === 2 ? Number(awayLeg1) : null,
            });
            setResult(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-6xl mx-auto space-y-10">

            {/* Header Banner */}
            <div className="relative flex items-center justify-between overflow-hidden rounded-3xl border border-slate-800 bg-gradient-to-r from-blue-900/40 via-indigo-950/40 to-slate-900 p-8 shadow-2xl">
                <div className="relative z-10 space-y-2">
                    <div className="inline-flex items-center space-x-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-400">
                        <Sparkles size={14} />
                        <span>Instant UCL Match Intelligence</span>
                    </div>
                    <h1 className="text-3xl font-extrabold tracking-tight text-white">Live Match Analysis</h1>
                    <p className="max-w-xl text-sm text-slate-400">
                        Pilih laga unggulan di bawah ini, atur konfigurasi leg dan skor Leg 1 secara dinamis, lalu biarkan AI Agent menganalisisnya.
                    </p>
                </div>
                <div className="relative hidden h-20 w-20 shrink-0 md:block opacity-80">
                    <Trophy size={80} className="text-blue-400 drop-shadow-[0_0_15px_rgba(59,130,246,0.5)]" />
                </div>
            </div>

            {/* Grid Laga Unggulan */}
            <div className="space-y-4">
                <h2 className="text-lg font-semibold text-slate-200">Daftar Pertandingan Unggulan</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {marqueeFixtures.map((match, idx) => (
                        <MatchCard
                            key={idx}
                            homeTeam={match.home}
                            awayTeam={match.away}
                            stage={match.stage}
                            homeLogo={match.homeLogo}
                            awayLogo={match.awayLogo}
                            onSelect={() => handleSelectMatch(match)}
                        />
                    ))}
                </div>
            </div>

            {/* Panel Konfigurasi & Analisis Interaktif */}
            {selectedMatch && (
                <div className="bg-slate-900 border border-slate-800 p-8 rounded-3xl shadow-2xl space-y-6">
                    <div className="flex justify-between items-center border-b border-slate-800 pb-4">
                        <div>
                            <span className="text-xs font-semibold text-blue-400 uppercase tracking-widest">{selectedMatch.stage}</span>
                            <h2 className="text-2xl font-bold text-white mt-1">{selectedMatch.home} vs {selectedMatch.away}</h2>
                        </div>
                        <button
                            onClick={() => setSelectedMatch(null)}
                            className="text-slate-400 hover:text-white bg-slate-800 px-4 py-2 rounded-xl text-xs transition-colors cursor-pointer"
                        >
                            Tutup ✕
                        </button>
                    </div>

                    {/* Form Input Dinamis */}
                    <form onSubmit={handleAnalyze} className="bg-slate-950 p-6 rounded-2xl border border-slate-800 space-y-4">
                        <div className="flex flex-wrap gap-6 items-center">
                            <div>
                                <label className="block text-xs font-medium text-slate-400 mb-1">Pilih Leg</label>
                                <select
                                    value={matchLeg}
                                    onChange={(e) => setMatchLeg(Number(e.target.value))}
                                    className="bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-sm text-white focus:outline-none"
                                >
                                    <option value={1}>Leg 1 (Laga Tunggal)</option>
                                    <option value={2}>Leg 2 (Agregat)</option>
                                </select>
                            </div>

                            {matchLeg === 2 && (
                                <div className="flex items-center gap-4 bg-slate-900/60 p-3 rounded-xl border border-slate-800/80">
                                    <div>
                                        <label className="block text-xs font-medium text-slate-400 mb-1">Gol Leg 1 ({selectedMatch.home})</label>
                                        <div className="flex items-center gap-2">
                                            <button type="button" onClick={() => setHomeLeg1(Math.max(0, homeLeg1 - 1))} className="px-2.5 py-1 bg-slate-800 rounded-lg text-white cursor-pointer">-</button>
                                            <span className="w-8 text-center font-bold text-white">{homeLeg1}</span>
                                            <button type="button" onClick={() => setHomeLeg1(homeLeg1 + 1)} className="px-2.5 py-1 bg-slate-800 rounded-lg text-white cursor-pointer">+</button>
                                        </div>
                                    </div>
                                    <span className="text-xs font-bold text-slate-500 mt-5">VS</span>
                                    <div>
                                        <label className="block text-xs font-medium text-slate-400 mb-1">Gol Leg 1 ({selectedMatch.away})</label>
                                        <div className="flex items-center gap-2">
                                            <button type="button" onClick={() => setAwayLeg1(Math.max(0, awayLeg1 - 1))} className="px-2.5 py-1 bg-slate-800 rounded-lg text-white cursor-pointer">-</button>
                                            <span className="w-8 text-center font-bold text-white">{awayLeg1}</span>
                                            <button type="button" onClick={() => setAwayLeg1(awayLeg1 + 1)} className="px-2.5 py-1 bg-slate-800 rounded-lg text-white cursor-pointer">+</button>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-medium py-3 rounded-xl transition-all text-xs cursor-pointer disabled:opacity-50 shadow-lg shadow-blue-600/20"
                        >
                            {loading ? '🤖 AI Agent sedang menghitung...' : 'Mulai Analisis AI untuk Laga Ini ⚡'}
                        </button>
                    </form>

                    {/* Hasil Prediksi */}
                    {loading ? (
                        <div className="py-12 text-center text-slate-400 animate-pulse font-medium">
                            🤖 AI Agent sedang memproses data historis dan menghitung probabilitas XGBoost...
                        </div>
                    ) : (
                        <PredictionResult
                            homeTeam={selectedMatch.home}
                            awayTeam={selectedMatch.away}
                            result={result}
                        />
                    )}
                </div>
            )}

        </div>
    );
}