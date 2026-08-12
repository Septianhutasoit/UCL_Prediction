import React from 'react';
import { teams, getTeamLogo } from '@/lib/teams';
import { ArrowLeftRight } from 'lucide-react';
import Logo from '@/components/Logo';

interface TeamPickerProps {
    homeTeam: string;
    awayTeam: string;
    selecting: 'home' | 'away';
    setSelecting: (s: 'home' | 'away') => void;
    swapTeams: () => void;
    handlePick: (name: string) => void;
}

export default function TeamPicker({
    homeTeam,
    awayTeam,
    selecting,
    setSelecting,
    swapTeams,
    handlePick,
}: TeamPickerProps) {
    return (
        <div className="space-y-6 rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-xl md:p-8">
            {/* Versus panel */}
            <div className="grid grid-cols-1 items-center gap-4 md:grid-cols-[1fr_auto_1fr]">
                <button
                    type="button"
                    onClick={() => setSelecting('home')}
                    className={`flex items-center gap-4 rounded-2xl border-2 p-5 text-left transition-all cursor-pointer ${selecting === 'home'
                            ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/10'
                            : 'border-slate-800 bg-slate-950 hover:border-slate-700'
                        }`}
                >
                    <Logo src={getTeamLogo(homeTeam)} alt={homeTeam} size={56} />
                    <div>
                        <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                            Tim Kandang
                        </span>
                        <span className="text-lg font-bold text-white">{homeTeam}</span>
                    </div>
                </button>

                <div className="flex items-center justify-center gap-3 md:flex-col">
                    <span className="text-xl font-black text-slate-600">VS</span>
                    <button
                        type="button"
                        onClick={swapTeams}
                        aria-label="Tukar tim kandang & tandang"
                        className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-700 bg-slate-800 text-slate-400 shadow transition-colors hover:border-blue-500/50 hover:text-blue-400 cursor-pointer"
                    >
                        <ArrowLeftRight size={15} />
                    </button>
                </div>

                <button
                    type="button"
                    onClick={() => setSelecting('away')}
                    className={`flex items-center gap-4 rounded-2xl border-2 p-5 text-left transition-all md:flex-row-reverse md:text-right cursor-pointer ${selecting === 'away'
                            ? 'border-indigo-500 bg-indigo-500/10 shadow-lg shadow-indigo-500/10'
                            : 'border-slate-800 bg-slate-950 hover:border-slate-700'
                        }`}
                >
                    <Logo src={getTeamLogo(awayTeam)} alt={awayTeam} size={56} />
                    <div>
                        <span className="block text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                            Tim Tandang
                        </span>
                        <span className="text-lg font-bold text-white">{awayTeam}</span>
                    </div>
                </button>
            </div>

            <p className="text-xs text-slate-500">
                Sedang memilih untuk:{' '}
                <span className={`font-semibold ${selecting === 'home' ? 'text-blue-400' : 'text-indigo-400'}`}>
                    {selecting === 'home' ? 'Tim Kandang' : 'Tim Tandang'}
                </span>
                <span className="text-slate-600"> — klik klub di bawah, atau klik kartu di atas untuk ganti sisi.</span>
            </p>

            {/* Grid klub */}
            <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-9">
                {teams.map((team) => {
                    const isHome = team.name === homeTeam;
                    const isAway = team.name === awayTeam;
                    return (
                        <button
                            key={team.name}
                            type="button"
                            onClick={() => handlePick(team.name)}
                            className={`group flex flex-col items-center gap-2 rounded-xl border p-3 transition-all cursor-pointer ${isHome
                                    ? 'border-blue-500 bg-blue-500/10'
                                    : isAway
                                        ? 'border-indigo-500 bg-indigo-500/10'
                                        : 'border-slate-800 bg-slate-950 hover:border-slate-700 hover:bg-slate-900'
                                }`}
                        >
                            <Logo
                                src={team.logo}
                                alt={team.name}
                                size={36}
                                className="transition-transform group-hover:scale-110"
                            />
                            <span className="truncate text-center text-[10px] font-medium leading-tight text-slate-400">
                                {team.name}
                            </span>
                            {isHome && <span className="text-[9px] font-bold uppercase text-blue-400">Home</span>}
                            {isAway && <span className="text-[9px] font-bold uppercase text-indigo-400">Away</span>}
                        </button>
                    );
                })}
            </div>
        </div>
    );
}