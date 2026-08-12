import React from 'react';
import Logo from '@/components/Logo';
import { getTeamLogo } from '@/lib/teams';
import { Minus, Plus } from 'lucide-react';

function ScoreStepper({
    team,
    logo,
    value,
    onChange,
    align = 'left',
}: {
    team: string;
    logo?: string;
    value: number;
    onChange: (v: number) => void;
    align?: 'left' | 'right';
}) {
    return (
        <div className={`flex flex-col items-center gap-2 ${align === 'right' ? 'sm:items-end' : 'sm:items-start'}`}>
            <div className={`flex items-center gap-2 ${align === 'right' ? 'sm:flex-row-reverse' : ''}`}>
                <Logo src={logo} alt={team} size={24} />
                <span className="max-w-[110px] truncate text-xs font-medium text-slate-400 sm:max-w-[140px]">{team}</span>
            </div>
            <div className="flex items-center gap-2">
                <button
                    type="button"
                    onClick={() => onChange(Math.max(0, value - 1))}
                    className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-800 bg-slate-900 text-slate-400 transition-colors hover:border-blue-500/40 hover:text-blue-400 cursor-pointer"
                >
                    <Minus size={14} />
                </button>
                <span className="w-10 text-center text-2xl font-black text-white">{value}</span>
                <button
                    type="button"
                    onClick={() => onChange(value + 1)}
                    className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-800 bg-slate-900 text-slate-400 transition-colors hover:border-blue-500/40 hover:text-blue-400 cursor-pointer"
                >
                    <Plus size={14} />
                </button>
            </div>
        </div>
    );
}

interface MatchConfigFormProps {
    homeTeam: string;
    awayTeam: string;
    matchLeg: number;
    setMatchLeg: (leg: number) => void;
    homeLeg1: number;
    setHomeLeg1: (v: number) => void;
    awayLeg1: number;
    setAwayLeg1: (v: number) => void;
    loading: boolean;
    error: string;
    onPredict: (e: React.FormEvent) => void;
}

export default function MatchConfigForm({
    homeTeam,
    awayTeam,
    matchLeg,
    setMatchLeg,
    homeLeg1,
    setHomeLeg1,
    awayLeg1,
    setAwayLeg1,
    loading,
    error,
    onPredict,
}: MatchConfigFormProps) {
    return (
        <form onSubmit={onPredict} className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
            <div className="mb-5 flex items-center justify-between">
                <h2 className="text-base font-semibold text-slate-200">Konfigurasi Pertandingan</h2>
                {matchLeg === 2 && (
                    <span className="text-xs text-slate-500">
                        Agregat saat ini:{' '}
                        <span className="font-semibold text-slate-300">
                            {homeLeg1}–{awayLeg1}
                        </span>{' '}
                        {homeLeg1 !== awayLeg1 && (
                            <span className={homeLeg1 > awayLeg1 ? 'text-blue-400' : 'text-indigo-400'}>
                                ({homeLeg1 > awayLeg1 ? homeTeam : awayTeam} unggul)
                            </span>
                        )}
                        {homeLeg1 === awayLeg1 && <span className="text-amber-400">(imbang)</span>}
                    </span>
                )}
            </div>

            <div className="mb-5 inline-flex rounded-xl border border-slate-800 bg-slate-950 p-1">
                <button
                    type="button"
                    onClick={() => setMatchLeg(1)}
                    className={`rounded-lg px-4 py-2 text-sm font-medium transition-all cursor-pointer ${matchLeg === 1 ? 'bg-blue-600 text-white shadow shadow-blue-600/30' : 'text-slate-400 hover:text-slate-200'
                        }`}
                >
                    Leg 1 — Laga Tunggal
                </button>
                <button
                    type="button"
                    onClick={() => setMatchLeg(2)}
                    className={`rounded-lg px-4 py-2 text-sm font-medium transition-all cursor-pointer ${matchLeg === 2 ? 'bg-blue-600 text-white shadow shadow-blue-600/30' : 'text-slate-400 hover:text-slate-200'
                        }`}
                >
                    Leg 2 — Agregat Dua Laga
                </button>
            </div>
            <p className="-mt-2 mb-5 text-xs text-slate-500">
                {matchLeg === 1
                    ? 'Prediksi dihitung dari satu pertandingan langsung.'
                    : 'Masukkan skor Leg 1 di bawah — sistem otomatis menghitung agregat & keunggulan gol tandang.'}
            </p>

            {matchLeg === 2 && (
                <div className="mb-5 flex items-center justify-center gap-6 rounded-2xl border border-slate-800 bg-slate-950 p-5 sm:gap-10">
                    <ScoreStepper team={homeTeam} logo={getTeamLogo(homeTeam)} value={homeLeg1} onChange={setHomeLeg1} />
                    <span className="text-sm font-bold text-slate-600">LEG 1</span>
                    <ScoreStepper team={awayTeam} logo={getTeamLogo(awayTeam)} value={awayLeg1} onChange={setAwayLeg1} align="right" />
                </div>
            )}

            <button
                type="submit"
                disabled={loading}
                className="w-full cursor-pointer rounded-xl bg-blue-600 py-3 font-medium text-white shadow-lg shadow-blue-600/20 transition-all hover:bg-blue-500 disabled:opacity-50"
            >
                {loading ? 'Menganalisis Data AI...' : 'Jalankan Prediksi 🚀'}
            </button>

            {error && <p className="mt-4 text-xs text-red-400">{error}</p>}
        </form>
    );
}