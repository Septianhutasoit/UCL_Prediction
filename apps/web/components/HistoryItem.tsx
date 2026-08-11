import React from 'react';
import { PredictionResponse } from '@/lib/types';

interface HistoryItemProps {
    item: {
        id: number;
        date: string;
        homeTeam: string;
        awayTeam: string;
        matchLeg: number;
        result: PredictionResponse;
    };
    onDelete: (id: number) => void;
}

export default function HistoryItem({ item, onDelete }: HistoryItemProps) {
    const { homeTeam, awayTeam, matchLeg, result } = item;

    return (
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6">

            {/* Info Utama */}
            <div className="space-y-1">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span className="bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded-md font-semibold border border-blue-500/20">
                        Leg {matchLeg}
                    </span>
                    <span>• {item.date}</span>
                </div>
                <h3 className="text-lg font-bold text-white">
                    {homeTeam} vs {awayTeam}
                </h3>
            </div>

            {/* Probabilitas & Tombol Hapus */}
            <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end">
                <div className="flex gap-3 text-center text-xs">
                    <div className="bg-slate-950 px-3 py-2 rounded-xl border border-slate-800">
                        <div className="font-bold text-blue-400">{(result.home_win_prob * 100).toFixed(1)}%</div>
                        <div className="text-[10px] text-slate-500">Home</div>
                    </div>
                    <div className="bg-slate-950 px-3 py-2 rounded-xl border border-slate-800">
                        <div className="font-bold text-amber-400">{(result.draw_prob * 100).toFixed(1)}%</div>
                        <div className="text-[10px] text-slate-500">Draw</div>
                    </div>
                    <div className="bg-slate-950 px-3 py-2 rounded-xl border border-slate-800">
                        <div className="font-bold text-indigo-400">{(result.away_win_prob * 100).toFixed(1)}%</div>
                        <div className="text-[10px] text-slate-500">Away</div>
                    </div>
                </div>

                <button
                    onClick={() => onDelete(item.id)}
                    className="text-slate-500 hover:text-red-400 bg-slate-800/60 hover:bg-red-500/10 p-2.5 rounded-xl transition-colors cursor-pointer"
                    title="Hapus riwayat ini"
                >
                    🗑️
                </button>
            </div>

        </div>
    );
}