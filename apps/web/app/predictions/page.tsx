'use client';

import React, { useMemo, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import MatchCard from '@/components/MatchCard';
import Logo from '@/components/Logo';
import { getTeamLogo } from '@/lib/teams';
import { fetchPrediction } from '@/lib/api';
import { PredictionResponse } from '@/lib/types';

interface Fixture {
    home: string;
    away: string;
    stage: string;
}

// Daftar laga unggulan (marquee fixtures) UCL
const marqueeFixtures: Fixture[] = [
    { home: 'Real Madrid', away: 'Manchester City', stage: 'Quarter-Final Leg 2' },
    { home: 'Bayern Munich', away: 'Arsenal', stage: 'Quarter-Final Leg 2' },
    { home: 'Barcelona', away: 'Paris Saint-Germain', stage: 'Quarter-Final Leg 2' },
    { home: 'Inter Milan', away: 'Atlético Madrid', stage: 'Round of 16 Leg 2' },
    { home: 'Juventus', away: 'Benfica', stage: 'League Phase' },
    { home: 'Liverpool', away: 'Borussia Dortmund', stage: 'League Phase' },
];

const stages = ['Semua', ...Array.from(new Set(marqueeFixtures.map((f) => f.stage)))];

function ProbabilityBar({
    homeLabel,
    awayLabel,
    homePct,
    drawPct,
    awayPct,
}: {
    homeLabel: string;
    awayLabel: string;
    homePct: number;
    drawPct: number;
    awayPct: number;
}) {
    return (
        <div className="space-y-2">
            <div className="flex justify-between text-xs font-semibold text-slate-400">
                <span className="text-blue-400">{homeLabel}</span>
                <span className="text-amber-400">Seri</span>
                <span className="text-indigo-400">{awayLabel}</span>
            </div>
            <div className="flex h-3 w-full overflow-hidden rounded-full bg-slate-950">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${homePct}%` }}
                    transition={{ duration: 0.6, ease: 'easeOut' }}
                    className="bg-blue-500"
                />
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${drawPct}%` }}
                    transition={{ duration: 0.6, ease: 'easeOut', delay: 0.05 }}
                    className="bg-amber-500"
                />
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${awayPct}%` }}
                    transition={{ duration: 0.6, ease: 'easeOut', delay: 0.1 }}
                    className="bg-indigo-500"
                />
            </div>
            <div className="flex justify-between text-[11px] text-slate-500">
                <span>{homePct.toFixed(1)}%</span>
                <span>{drawPct.toFixed(1)}%</span>
                <span>{awayPct.toFixed(1)}%</span>
            </div>
        </div>
    );
}

export default function LiveAnalysisPage() {
    const [activeStage, setActiveStage] = useState('Semua');
    const [selectedMatch, setSelectedMatch] = useState<Fixture | null>(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<PredictionResponse | null>(null);
    const resultRef = useRef<HTMLDivElement>(null);

    const filteredFixtures = useMemo(
        () => (activeStage === 'Semua' ? marqueeFixtures : marqueeFixtures.filter((f) => f.stage === activeStage)),
        [activeStage]
    );

    const handleAnalyze = async (match: Fixture) => {
        setSelectedMatch(match);
        setLoading(true);
        setResult(null);

        // beri waktu render dulu supaya scroll target sudah ada di DOM
        setTimeout(() => resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);

        try {
            const data = await fetchPrediction({
                home_team: match.home,
                away_team: match.away,
                match_leg: 2,
                home_leg1_score: 1,
                away_leg1_score: 1,
                home_win_rate: 0.75,
                away_win_rate: 0.7,
                elo_difference: 30.0,
            });
            setResult(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="mx-auto max-w-6xl space-y-8">
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-white">Live Match Analysis</h1>
                <p className="mt-1 text-slate-400">
                    Pilih pertandingan marquee Liga Champions di bawah ini untuk melihat analisis AI instan dari Backend Go
                    &amp; XGBoost.
                </p>
            </div>

            {/* Filter Fase Pertandingan */}
            <div className="flex flex-wrap gap-2">
                {stages.map((stage) => (
                    <button
                        key={stage}
                        onClick={() => setActiveStage(stage)}
                        className={`rounded-xl border px-4 py-2 text-xs font-semibold transition-all ${activeStage === stage
                                ? 'border-blue-500 bg-blue-600 text-white shadow shadow-blue-600/30'
                                : 'border-slate-800 bg-slate-900 text-slate-400 hover:border-slate-700 hover:text-slate-200'
                            }`}
                    >
                        {stage}
                    </button>
                ))}
            </div>

            {/* Grid Daftar Pertandingan */}
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
                {filteredFixtures.map((match, idx) => (
                    <MatchCard
                        key={idx}
                        homeTeam={match.home}
                        awayTeam={match.away}
                        stage={match.stage}
                        active={selectedMatch?.home === match.home && selectedMatch?.away === match.away}
                        onSelect={() => handleAnalyze(match)}
                    />
                ))}
                {filteredFixtures.length === 0 && (
                    <div className="col-span-full rounded-2xl border border-dashed border-slate-800 p-10 text-center text-sm text-slate-500">
                        Tidak ada laga di fase ini.
                    </div>
                )}
            </div>

            {/* Panel Hasil Analisis */}
            <div ref={resultRef} className="scroll-mt-8">
                <AnimatePresence>
                    {selectedMatch && (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.25 }}
                            className="mt-2 space-y-6 rounded-3xl border border-slate-800 bg-slate-900 p-8 shadow-2xl"
                        >
                            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                                <div className="flex items-center gap-4">
                                    <div className="hidden items-center gap-2 sm:flex">
                                        <Logo src={getTeamLogo(selectedMatch.home)} alt={selectedMatch.home} size={32} />
                                        <span className="text-xs font-bold text-slate-600">VS</span>
                                        <Logo src={getTeamLogo(selectedMatch.away)} alt={selectedMatch.away} size={32} />
                                    </div>
                                    <div>
                                        <span className="text-xs font-semibold uppercase tracking-widest text-blue-400">
                                            {selectedMatch.stage}
                                        </span>
                                        <h2 className="mt-1 text-2xl font-bold text-white">
                                            {selectedMatch.home} vs {selectedMatch.away}
                                        </h2>
                                    </div>
                                </div>
                                <button
                                    onClick={() => {
                                        setSelectedMatch(null);
                                        setResult(null);
                                    }}
                                    className="cursor-pointer rounded-xl bg-slate-800 px-3.5 py-2 text-xs text-slate-400 transition-colors hover:text-white"
                                >
                                    Tutup ✕
                                </button>
                            </div>

                            {loading ? (
                                <div className="space-y-3 py-8">
                                    <div className="mx-auto h-2 w-2/3 animate-pulse rounded-full bg-slate-800" />
                                    <div className="mx-auto h-2 w-1/2 animate-pulse rounded-full bg-slate-800" />
                                    <p className="pt-4 text-center text-sm text-slate-400">
                                        ⚡ Menganalisis taktik pertandingan dan menghitung probabilitas XGBoost...
                                    </p>
                                </div>
                            ) : result ? (
                                <div className="space-y-6">
                                    {/* Probability bar visual */}
                                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-5">
                                        <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                            Probabilitas Hasil Laga
                                        </h4>
                                        <ProbabilityBar
                                            homeLabel={selectedMatch.home}
                                            awayLabel={selectedMatch.away}
                                            homePct={result.home_win_prob * 100}
                                            drawPct={result.draw_prob * 100}
                                            awayPct={result.away_win_prob * 100}
                                        />
                                    </div>

                                    {/* Kartu angka pendukung */}
                                    <div className="grid grid-cols-3 gap-4 text-center">
                                        <div className="flex flex-col items-center rounded-2xl border border-slate-800 bg-slate-950 p-5">
                                            <Logo src={getTeamLogo(selectedMatch.home)} alt={selectedMatch.home} size={28} className="mb-2" />
                                            <div className="text-2xl font-bold text-blue-400">
                                                {(result.home_win_prob * 100).toFixed(1)}%
                                            </div>
                                            <div className="mt-1 text-xs text-slate-400">{selectedMatch.home} Menang</div>
                                        </div>
                                        <div className="flex flex-col items-center justify-center rounded-2xl border border-slate-800 bg-slate-950 p-5">
                                            <div className="text-2xl font-bold text-amber-400">{(result.draw_prob * 100).toFixed(1)}%</div>
                                            <div className="mt-1 text-xs text-slate-400">Seri (Draw)</div>
                                        </div>
                                        <div className="flex flex-col items-center rounded-2xl border border-slate-800 bg-slate-950 p-5">
                                            <Logo src={getTeamLogo(selectedMatch.away)} alt={selectedMatch.away} size={28} className="mb-2" />
                                            <div className="text-2xl font-bold text-indigo-400">
                                                {(result.away_win_prob * 100).toFixed(1)}%
                                            </div>
                                            <div className="mt-1 text-xs text-slate-400">{selectedMatch.away} Menang</div>
                                        </div>
                                    </div>

                                    {result.home_qualification_prob !== null && result.home_qualification_prob !== undefined && (
                                        <div className="grid grid-cols-2 gap-4 text-center">
                                            <div className="rounded-2xl border border-blue-900/40 bg-blue-950/20 p-4">
                                                <div className="text-xl font-bold text-blue-300">
                                                    {(result.home_qualification_prob * 100).toFixed(1)}%
                                                </div>
                                                <div className="mt-1 text-xs text-blue-400/80">{selectedMatch.home} Lolos</div>
                                            </div>
                                            <div className="rounded-2xl border border-indigo-900/40 bg-indigo-950/20 p-4">
                                                <div className="text-xl font-bold text-indigo-300">
                                                    {(result.away_qualification_prob! * 100).toFixed(1)}%
                                                </div>
                                                <div className="mt-1 text-xs text-indigo-400/80">{selectedMatch.away} Lolos</div>
                                            </div>
                                        </div>
                                    )}

                                    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-6">
                                        <h4 className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                            Analisis Taktikal AI
                                        </h4>
                                        <p className="text-sm leading-relaxed text-slate-300">{result.ai_analysis}</p>
                                    </div>
                                </div>
                            ) : null}
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </div>
    );
}