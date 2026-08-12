import React from 'react';
import Logo from '@/components/Logo';

export default function MatchHero() {
    return (
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
    );
}