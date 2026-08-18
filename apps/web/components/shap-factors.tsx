import React from 'react';

interface ShapFactor {
    feature: string;
    value: number;
    impact: string;
}

interface ShapFactorsProps {
    factors: ShapFactor[];
}

export default function ShapFactors({ factors }: ShapFactorsProps) {
    if (!factors || factors.length === 0) return null;

    return (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-xl space-y-4">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                📊 SHAP Explainable AI (Faktor Penentu Utama)
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {factors.map((f, i) => (
                    <div key={i} className="flex items-center justify-between bg-slate-950 p-3.5 rounded-xl border border-slate-800/60">
                        <span className="text-xs font-medium text-slate-300">{f.feature}</span>
                        <span className={`text-xs font-bold px-2.5 py-1 rounded-md ${f.impact === 'positif'
                                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                            }`}>
                            {f.impact === 'positif' ? '+' : ''}{f.value.toFixed(2)}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}