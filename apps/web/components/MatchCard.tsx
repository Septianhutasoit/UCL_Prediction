'use client';

import Logo from '@/components/Logo';
import { getTeamLogo } from '@/lib/teams';

interface MatchCardProps {
    homeTeam: string;
    awayTeam: string;
    stage: string;
    active?: boolean;
    onSelect: () => void;
}

const stageStyle: Record<string, string> = {
    'Quarter-Final Leg 2': 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    'Round of 16 Leg 2': 'bg-purple-500/10 text-purple-400 border-purple-500/20',
    'League Phase': 'bg-blue-500/10 text-blue-400 border-blue-500/20',
};

export default function MatchCard({ homeTeam, awayTeam, stage, active, onSelect }: MatchCardProps) {
    const badgeClass = stageStyle[stage] ?? 'bg-slate-500/10 text-slate-400 border-slate-500/20';

    return (
        <div
            className={`group flex flex-col justify-between space-y-5 rounded-3xl border p-6 shadow-xl transition-all ${active
                    ? 'border-blue-500/60 bg-blue-500/5 shadow-blue-500/10'
                    : 'border-slate-800 bg-slate-900 hover:border-blue-500/40'
                }`}
        >
            {/* Header Kartu */}
            <div className="flex items-center justify-between text-xs">
                <span className={`rounded-full border px-3 py-1 font-semibold ${badgeClass}`}>{stage}</span>
                <span className="flex items-center gap-1.5 font-medium text-emerald-400">
                    <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />
                    Ready for AI
                </span>
            </div>

            {/* Tim & Logo */}
            <div className="flex items-center justify-between py-2">
                <div className="flex w-1/3 flex-col items-center space-y-2">
                    <Logo src={getTeamLogo(homeTeam)} alt={homeTeam} size={48} />
                    <span className="w-full truncate text-center text-xs font-bold text-slate-200">{homeTeam}</span>
                </div>

                <div className="text-base font-black italic text-slate-600">VS</div>

                <div className="flex w-1/3 flex-col items-center space-y-2">
                    <Logo src={getTeamLogo(awayTeam)} alt={awayTeam} size={48} />
                    <span className="w-full truncate text-center text-xs font-bold text-slate-200">{awayTeam}</span>
                </div>
            </div>

            {/* Tombol Aksi */}
            <button
                onClick={onSelect}
                className={`w-full cursor-pointer rounded-2xl border py-3 text-xs font-semibold shadow-sm transition-all ${active
                        ? 'border-blue-500/40 bg-blue-600 text-white'
                        : 'border-slate-700/60 bg-slate-800 text-slate-200 group-hover:border-blue-500/30 hover:bg-blue-600 hover:text-white'
                    }`}
            >
                {active ? 'Sedang Dianalisis ⚡' : 'Analisis Laga Ini ⚡'}
            </button>
        </div>
    );
}