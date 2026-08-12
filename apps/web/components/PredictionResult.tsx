import React from 'react';
import { PredictionResponse } from '@/lib/types';
import Logo from '@/components/Logo';
import { getTeamLogo } from '@/lib/teams';

interface PredictionResultProps {
    homeTeam: string;
    awayTeam: string;
    result: PredictionResponse | null;
}

export default function PredictionResult({ homeTeam, awayTeam, result }: PredictionResultProps) {
    if (!result) {
        return (
            <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-800/60 bg-slate-900/50 p-12 text-center text-slate-500">
                <span className="mb-2 text-4xl">⚽</span>
                <p className="text-sm">Silakan pilih klub, konfigurasi leg, lalu klik &quot;Jalankan Prediksi&quot;.</p>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="space-y-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
                <div>
                    <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                        Probabilitas Hasil Laga
                    </h3>
                    <div className="grid grid-cols-3 gap-4 text-center">
                        <div className="flex flex-col items-center justify-center rounded-xl border border-slate-800/60 bg-slate-950 p-4">
                            <Logo src={getTeamLogo(homeTeam)} alt={homeTeam} size={32} className="mb-2" />
                            <div className="text-2xl font-bold text-blue-400">
                                {(result.home_win_prob * 100).toFixed(1)}%
                            </div>
                            <div className="mt-1 text-xs text-slate-400">{homeTeam} Menang</div>
                        </div>

                        <div className="flex flex-col items-center justify-center rounded-xl border border-slate-800/60 bg-slate-950 p-4">
                            <div className="text-2xl font-bold text-amber-400">{(result.draw_prob * 100).toFixed(1)}%</div>
                            <div className="mt-1 text-xs text-slate-400">Seri (Draw)</div>
                        </div>

                        <div className="flex flex-col items-center justify-center rounded-xl border border-slate-800/60 bg-slate-950 p-4">
                            <Logo src={getTeamLogo(awayTeam)} alt={awayTeam} size={32} className="mb-2" />
                            <div className="text-2xl font-bold text-indigo-400">
                                {(result.away_win_prob * 100).toFixed(1)}%
                            </div>
                            <div className="mt-1 text-xs text-slate-400">{awayTeam} Menang</div>
                        </div>
                    </div>
                </div>

                {result.home_qualification_prob !== null && result.home_qualification_prob !== undefined && (
                    <div className="border-t border-slate-800 pt-6">
                        <h3 className="mb-4 text-xs font-semibold uppercase tracking-wider text-slate-400">
                            Peluang Lolos ke Babak Berikutnya
                        </h3>
                        <div className="grid grid-cols-2 gap-4 text-center">
                            <div className="rounded-xl border border-blue-900/40 bg-blue-950/20 p-4">
                                <div className="text-xl font-bold text-blue-300">
                                    {(result.home_qualification_prob * 100).toFixed(1)}%
                                </div>
                                <div className="mt-1 text-xs text-blue-400/80">{homeTeam} Lolos</div>
                            </div>
                            <div className="rounded-xl border border-indigo-900/40 bg-indigo-950/20 p-4">
                                <div className="text-xl font-bold text-indigo-300">
                                    {(result.away_qualification_prob! * 100).toFixed(1)}%
                                </div>
                                <div className="mt-1 text-xs text-indigo-400/80">{awayTeam} Lolos</div>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
                <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Analisis Taktikal AI
                </h3>
                <p className="rounded-xl border border-slate-800/60 bg-slate-950 p-4 text-sm leading-relaxed text-slate-300">
                    {result.ai_analysis}
                </p>
            </div>
        </div>
    );
}