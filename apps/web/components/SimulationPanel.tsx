import React, { useState } from 'react';

interface SimulationPanelProps {
    homeTeam: string;
    awayTeam: string;
    matchLeg: number;
    homeLeg1Score?: number | null;
    awayLeg1Score?: number | null;
}

export default function SimulationPanel({
    homeTeam,
    awayTeam,
    matchLeg,
    homeLeg1Score,
    awayLeg1Score,
}: SimulationPanelProps) {
    const [scenarioResult, setScenarioResult] = useState<any | null>(null);
    const [loading, setLoading] = useState(false);

    const runSimulation = async (scenario: string) => {
        setLoading(true);
        setScenarioResult(null);

        try {
            // Memanggil endpoint simulasi di Backend Go (port 8080)
            const res = await fetch(`http://localhost:8080/api/v1/simulate?scenario=${scenario}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    home_team: homeTeam,
                    away_team: awayTeam,
                    match_leg: matchLeg,
                    home_leg1_score: homeLeg1Score,
                    away_leg1_score: awayLeg1Score,
                }),
            });

            if (!res.ok) throw new Error('Gagal menjalankan simulasi skenario');

            const data = await res.json();
            setScenarioResult(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl space-y-4">
            <div className="flex items-center justify-between">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    ⚡ What-if Scenario Simulator (Agent Tool)
                </h3>
                <span className="rounded-md border border-blue-500/20 bg-blue-500/10 px-2 py-0.5 text-[10px] font-semibold text-blue-400">
                    Interactive AI
                </span>
            </div>
            <p className="text-xs text-slate-500">
                Uji coba skenario alternatif untuk melihat bagaimana perubahan kondisi memengaruhi peluang kemenangan {homeTeam} vs {awayTeam}.
            </p>

            {/* Tombol Pilihan Skenario */}
            <div className="flex flex-wrap gap-3 pt-2">
                <button
                    type="button"
                    onClick={() => runSimulation('neutral_venue')}
                    disabled={loading}
                    className="cursor-pointer rounded-xl border border-slate-700 bg-slate-800 px-4 py-2.5 text-xs font-medium text-slate-300 transition-all hover:border-blue-500 hover:bg-blue-600 hover:text-white disabled:opacity-50"
                >
                    🏟️ Pindah ke Tempat Netral
                </button>
                <button
                    type="button"
                    onClick={() => runSimulation('aggressive_tactic')}
                    disabled={loading}
                    className="cursor-pointer rounded-xl border border-slate-700 bg-slate-800 px-4 py-2.5 text-xs font-medium text-slate-300 transition-all hover:border-blue-500 hover:bg-blue-600 hover:text-white disabled:opacity-50"
                >
                    🔥 Taktik All-Out Attack
                </button>
            </div>

            {loading && (
                <div className="py-4 text-center text-xs text-blue-400 animate-pulse">
                    🤖 AI Agent sedang menghitung ulang skenario...
                </div>
            )}

            {/* Hasil Simulasi Skenario */}
            {scenarioResult && (
                <div className="mt-4 space-y-3 rounded-xl border border-slate-800 bg-slate-950 p-4">
                    <div className="text-xs font-bold text-blue-400">{scenarioResult.scenario_name}</div>
                    <p className="text-xs leading-relaxed text-slate-300">{scenarioResult.explanation}</p>
                    <div className="flex justify-between border-t border-slate-800/60 pt-2 text-xs text-slate-400">
                        <span>Win (Normal): {(scenarioResult.baseline.home_win_prob * 100).toFixed(1)}%</span>
                        <span className="font-bold text-white">
                            Win (Skenario): {(scenarioResult.scenario_result.home_win_prob * 100).toFixed(1)}%{' '}
                            <span className={scenarioResult.probability_difference >= 0 ? 'text-emerald-400 ml-1.5' : 'text-red-400 ml-1.5'}>
                                ({scenarioResult.probability_difference >= 0 ? '+' : ''}{(scenarioResult.probability_difference * 100).toFixed(1)}%)
                            </span>
                        </span>
                    </div>
                </div>
            )}
        </div>
    );
}