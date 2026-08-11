'use client';

import React, { useState } from 'react';
import { fetchPrediction } from '@/lib/api';
import { PredictionResponse } from '@/lib/types';
import { teams, getTeamLogo } from '@/lib/teams';
import { ArrowLeftRight, Minus, Plus } from 'lucide-react';
import Logo from '@/components/Logo';

type Selecting = 'home' | 'away';

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
          className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-800 bg-slate-900 text-slate-400 transition-colors hover:border-blue-500/40 hover:text-blue-400"
          aria-label={`Kurangi gol ${team}`}
        >
          <Minus size={14} />
        </button>
        <span className="w-10 text-center text-2xl font-black text-white">{value}</span>
        <button
          type="button"
          onClick={() => onChange(value + 1)}
          className="flex h-8 w-8 items-center justify-center rounded-lg border border-slate-800 bg-slate-900 text-slate-400 transition-colors hover:border-blue-500/40 hover:text-blue-400"
          aria-label={`Tambah gol ${team}`}
        >
          <Plus size={14} />
        </button>
      </div>
    </div>
  );
}

export default function Home() {
  const [homeTeam, setHomeTeam] = useState('Real Madrid');
  const [awayTeam, setAwayTeam] = useState('Bayern Munich');
  const [selecting, setSelecting] = useState<Selecting>('home');

  const [matchLeg, setMatchLeg] = useState(2);
  const [homeLeg1, setHomeLeg1] = useState(1);
  const [awayLeg1, setAwayLeg1] = useState(2);

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [error, setError] = useState('');

  const handlePick = (name: string) => {
    if (selecting === 'home') {
      if (name === awayTeam) return;
      setHomeTeam(name);
      setSelecting('away');
    } else {
      if (name === homeTeam) return;
      setAwayTeam(name);
      setSelecting('home');
    }
  };

  const swapTeams = () => {
    setHomeTeam(awayTeam);
    setAwayTeam(homeTeam);
    setHomeLeg1(awayLeg1);
    setAwayLeg1(homeLeg1);
  };

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
    <div className="mx-auto max-w-6xl space-y-8">
      {/* Header Banner */}
      <div className="relative flex items-center justify-between overflow-hidden rounded-3xl border border-slate-800 bg-gradient-to-r from-blue-900/40 via-indigo-950/40 to-slate-900 p-8 shadow-2xl">
        <div className="relative z-10 space-y-2">
          <div className="inline-flex items-center space-x-2 rounded-full border border-blue-500/20 bg-blue-500/10 px-3 py-1 text-xs font-semibold text-blue-400">
            <span>⚽ UEFA Champions League AI Engine</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">Match Intelligence &amp; Prediction</h1>
          <p className="max-w-xl text-sm text-slate-400">
            Analisis taktik mendalam dan probabilitas hasil laga fase gugur ditenagai oleh Machine Learning XGBoost.
          </p>
        </div>
        <div className="relative hidden h-20 w-20 shrink-0 overflow-hidden rounded-2xl shadow-lg shadow-blue-500/20 md:block">
          <Logo src="/icon.png" alt="UEFA Champions League" size={80} className="h-full w-full" />
        </div>
      </div>

      {/* ===== ZONA PILIH TIM (gaya FIFA select screen) ===== */}
      <div className="space-y-6 rounded-3xl border border-slate-800 bg-slate-900 p-6 shadow-xl md:p-8">
        {/* Versus panel */}
        <div className="grid grid-cols-1 items-center gap-4 md:grid-cols-[1fr_auto_1fr]">
          <button
            type="button"
            onClick={() => setSelecting('home')}
            className={`flex items-center gap-4 rounded-2xl border-2 p-5 text-left transition-all ${
              selecting === 'home'
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
              className="flex h-9 w-9 items-center justify-center rounded-full border border-slate-700 bg-slate-800 text-slate-400 shadow transition-colors hover:border-blue-500/50 hover:text-blue-400"
            >
              <ArrowLeftRight size={15} />
            </button>
          </div>

          <button
            type="button"
            onClick={() => setSelecting('away')}
            className={`flex items-center gap-4 rounded-2xl border-2 p-5 text-left transition-all md:flex-row-reverse md:text-right ${
              selecting === 'away'
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

        {/* Petunjuk mode pilih aktif */}
        <p className="text-xs text-slate-500">
          Sedang memilih untuk:{' '}
          <span className={`font-semibold ${selecting === 'home' ? 'text-blue-400' : 'text-indigo-400'}`}>
            {selecting === 'home' ? 'Tim Kandang' : 'Tim Tandang'}
          </span>
          <span className="text-slate-600"> — klik klub di bawah, atau klik kartu di atas untuk ganti sisi.</span>
        </p>

        {/* Grid semua klub — semua kelihatan sekaligus, tidak lewat dropdown */}
        <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-9">
          {teams.map((team) => {
            const isHome = team.name === homeTeam;
            const isAway = team.name === awayTeam;
            return (
              <button
                key={team.name}
                type="button"
                onClick={() => handlePick(team.name)}
                className={`group flex flex-col items-center gap-2 rounded-xl border p-3 transition-all ${
                  isHome
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

      {/* ===== KONFIGURASI LAGA ===== */}
      <form onSubmit={handlePredict} className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
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

        {/* Segmented toggle: Leg 1 / Leg 2 */}
        <div className="mb-5 inline-flex rounded-xl border border-slate-800 bg-slate-950 p-1">
          <button
            type="button"
            onClick={() => setMatchLeg(1)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
              matchLeg === 1 ? 'bg-blue-600 text-white shadow shadow-blue-600/30' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Leg 1 — Laga Tunggal
          </button>
          <button
            type="button"
            onClick={() => setMatchLeg(2)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
              matchLeg === 2 ? 'bg-blue-600 text-white shadow shadow-blue-600/30' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Leg 2 — Agregat Dua Laga
          </button>
        </div>
        <p className="-mt-2 mb-5 text-xs text-slate-500">
          {matchLeg === 1
            ? 'Prediksi dihitung dari satu pertandingan langsung, tanpa hasil laga sebelumnya.'
            : 'Masukkan skor Leg 1 di bawah — sistem otomatis menghitung agregat & keunggulan gol tandang untuk memprediksi hasil kelolosan.'}
        </p>

        {/* Scoreboard skor Leg 1 — hanya muncul untuk mode Leg 2 */}
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

      {/* ===== HASIL PREDIKSI — full width di bawah ===== */}
      <div className="space-y-6">
        {result ? (
          <>
            {/* Kartu Probabilitas */}
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

            {/* Analisis AI */}
            <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl">
              <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">
                Analisis Taktikal AI
              </h3>
              <p className="rounded-xl border border-slate-800/60 bg-slate-950 p-4 text-sm leading-relaxed text-slate-300">
                {result.ai_analysis}
              </p>
            </div>
          </>
        ) : (
          <div className="flex flex-col items-center justify-center rounded-2xl border border-dashed border-slate-800/60 bg-slate-900/50 p-12 text-center text-slate-500">
            <span className="mb-2 text-4xl">⚽</span>
            <p className="text-sm">Silakan pilih klub, konfigurasi leg, lalu klik &quot;Jalankan Prediksi&quot;.</p>
          </div>
        )}
      </div>
    </div>
  );
}