'use client';

import React from 'react';

interface HistoryItemProps {
    item: any;
    onDelete: (id: any) => void;
}

export default function HistoryItem({ item, onDelete }: HistoryItemProps) {
    // Ekstraksi Data Aman (Mendukung format backend Go maupun localStorage tanpa crash)
    const homeTeam = item.homeTeam || item.home_team || 'Home Team';
    const awayTeam = item.awayTeam || item.away_team || 'Away Team';
    const matchLeg = item.matchLeg || item.match_leg || 1;
    const dateText = item.date || item.created_at || item.createdAt || 'Baru saja';
    const itemId = item.id;

    // Probabilitas Aman (Mencegah error 'result is undefined')
    const homeProb = item.result?.home_win_prob ?? item.home_win_prob ?? item.homeWinProb ?? 0.50;
    const drawProb = item.result?.draw_prob ?? item.draw_prob ?? item.drawProb ?? 0.25;
    const awayProb = item.result?.away_win_prob ?? item.away_win_prob ?? item.awayWinProb ?? 0.25;
    const analysis = item.result?.ai_analysis || item.ai_analysis || '';

    return (
        <div className="group relative overflow-hidden bg-slate-900/80 hover:bg-slate-900 border border-slate-800/80 hover:border-slate-700 p-6 rounded-3xl shadow-xl transition-all duration-300 backdrop-blur-md flex flex-col md:flex-row justify-between items-start md:items-center gap-6">

            {/* Kolom Kiri: Informasi Laga & Tanggal */}
            <div className="space-y-2 flex-1">
                <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span className="bg-blue-500/10 text-blue-400 px-2.5 py-0.5 rounded-lg font-bold border border-blue-500/20 text-[10px] tracking-wide uppercase">
                        Leg {matchLeg}
                    </span>
                    <span className="text-slate-500">•</span>
                    <span className="font-mono text-[11px] text-slate-400">{dateText}</span>
                </div>

                <h3 className="text-base md:text-lg font-extrabold text-white tracking-wide flex items-center gap-2">
                    <span className="text-blue-400">{homeTeam}</span>
                    <span className="text-xs text-slate-500 font-bold px-1">VS</span>
                    <span className="text-indigo-400">{awayTeam}</span>
                </h3>

                {analysis && (
                    <p className="text-[11px] text-slate-400 line-clamp-2 max-w-xl leading-relaxed">
                        {analysis}
                    </p>
                )}
            </div>

            {/* Kolom Kanan: Kartu Probabilitas & Tombol Aksi */}
            <div className="flex items-center gap-4 w-full md:w-auto justify-between md:justify-end pt-2 md:pt-0 border-t md:border-t-0 border-slate-800/60">

                {/* Pil Probabilitas */}
                <div className="flex items-center gap-2 text-center text-xs">
                    {/* Home Win */}
                    <div className="bg-slate-950/80 px-3.5 py-2 rounded-2xl border border-slate-800/80 min-w-[64px]">
                        <div className="font-bold text-blue-400 text-sm">
                            {(homeProb * 100).toFixed(1)}%
                        </div>
                        <div className="text-[9px] font-semibold text-slate-500 uppercase tracking-wider">Home</div>
                    </div>

                    {/* Draw */}
                    <div className="bg-slate-950/80 px-3.5 py-2 rounded-2xl border border-slate-800/80 min-w-[64px]">
                        <div className="font-bold text-amber-400 text-sm">
                            {(drawProb * 100).toFixed(1)}%
                        </div>
                        <div className="text-[9px] font-semibold text-slate-500 uppercase tracking-wider">Draw</div>
                    </div>

                    {/* Away Win */}
                    <div className="bg-slate-950/80 px-3.5 py-2 rounded-2xl border border-slate-800/80 min-w-[64px]">
                        <div className="font-bold text-indigo-400 text-sm">
                            {(awayProb * 100).toFixed(1)}%
                        </div>
                        <div className="text-[9px] font-semibold text-slate-500 uppercase tracking-wider">Away</div>
                    </div>
                </div>

                {/* Tombol Hapus */}
                <button
                    onClick={() => onDelete(itemId)}
                    className="text-slate-500 hover:text-red-400 bg-slate-950/60 hover:bg-red-500/10 border border-slate-800 hover:border-red-500/30 p-2.5 rounded-2xl transition-all duration-200 cursor-pointer shadow-sm active:scale-95"
                    title="Hapus riwayat pertandingan ini"
                >
                    🗑️
                </button>
            </div>

        </div>
    );
}