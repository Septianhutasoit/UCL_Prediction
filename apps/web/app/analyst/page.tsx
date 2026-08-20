'use client';

import React, { useState } from 'react';
import { teams, getTeamLogo } from '@/lib/teams';
import Logo from '@/components/Logo';
import { Send, Bot, User, Sparkles } from 'lucide-react';

export default function AnalystPage() {
    const [messages, setMessages] = useState<any[]>([
        { role: 'assistant', content: 'Halo! Saya ChampIntel Analyst Agent. Pilih dua klub di bawah dan tanyakan analisis taktik, prediksi, atau jalankan simulasi skenario (misal: "Bagaimana jika main di tempat netral?").' }
    ]);
    const [inputQuery, setInputQuery] = useState('');
    const [homeTeam, setHomeTeam] = useState('Real Madrid');
    const [awayTeam, setAwayTeam] = useState('Bayern Munich');
    const [loading, setLoading] = useState(false);

    const handleSendMessage = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!inputQuery.trim() || loading) return;

        const userMsg = inputQuery;
        setInputQuery('');
        setMessages((prev) => [...prev, { role: 'user', content: userMsg }]);
        setLoading(true);

        try {
            // Panggil endpoint Agent di FastAPI (port 8000)
            const res = await fetch('http://localhost:8000/agent/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: userMsg,
                    home_team: homeTeam,
                    away_team: awayTeam,
                    match_leg: 2,
                    home_leg1_score: 1,
                    away_leg1_score: 2,
                }),
            });

            if (!res.ok) throw new Error('Gagal terhubung ke AI Agent');

            const data = await res.json();
            setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
        } catch (err) {
            setMessages((prev) => [...prev, { role: 'assistant', content: 'Maaf, terjadi kesalahan saat menghubungi AI Agent. Pastikan FastAPI dan Backend menyala.' }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">

            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold tracking-tight text-white flex items-center gap-2">
                    <Sparkles className="text-blue-400" /> ChampIntel Analyst Agent
                </h1>
                <p className="text-slate-400 text-sm mt-1">
                    Asisten AI interaktif berbasis agent yang siap menjawab pertanyaan taktis seputar laga UEFA Champions League.
                </p>
            </div>

            {/* Konfigurasi Klub untuk Chat */}
            <div className="bg-slate-900 border border-slate-800 p-4 rounded-2xl flex items-center justify-between gap-4 shadow-xl">
                <div className="flex items-center gap-3 flex-wrap">
                    <span className="text-xs text-slate-400 font-semibold">Klub Fokus Laga:</span>

                    <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
                        <Logo src={getTeamLogo(homeTeam)} alt={homeTeam} size={20} />
                        <select
                            value={homeTeam}
                            onChange={(e) => setHomeTeam(e.target.value)}
                            className="bg-transparent text-xs text-white focus:outline-none cursor-pointer"
                        >
                            {teams.map(t => <option key={t.name} value={t.name} className="bg-slate-900 text-white">{t.name}</option>)}
                        </select>
                    </div>

                    <span className="text-xs text-slate-500 font-bold">VS</span>

                    <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
                        <Logo src={getTeamLogo(awayTeam)} alt={awayTeam} size={20} />
                        <select
                            value={awayTeam}
                            onChange={(e) => setAwayTeam(e.target.value)}
                            className="bg-transparent text-xs text-white focus:outline-none cursor-pointer"
                        >
                            {teams.map(t => <option key={t.name} value={t.name} className="bg-slate-900 text-white">{t.name}</option>)}
                        </select>
                    </div>
                </div>
            </div>

            {/* Chat Container */}
            <div className="bg-slate-900 border border-slate-800 rounded-3xl shadow-xl flex flex-col h-[550px] overflow-hidden">

                {/* Pesan Chat */}
                <div className="flex-1 overflow-y-auto p-6 space-y-4">
                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-indigo-600/30 text-indigo-400 border border-indigo-500/30'
                                }`}>
                                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                            </div>
                            <div className={`max-w-[85%] p-4 rounded-2xl text-sm leading-relaxed ${msg.role === 'user'
                                    ? 'bg-blue-600 text-white rounded-tr-none'
                                    : 'bg-slate-950 border border-slate-800 text-slate-200 rounded-tl-none shadow-md'
                                }`}>
                                <p>{msg.content}</p>
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-full bg-indigo-600/30 text-indigo-400 border border-indigo-500/30 flex items-center justify-center shrink-0">
                                <Bot size={16} />
                            </div>
                            <div className="bg-slate-950 border border-slate-800 p-4 rounded-2xl text-sm text-slate-400 animate-pulse">
                                🤖 AI Agent sedang merencanakan *workflow* dan memanggil *tools*...
                            </div>
                        </div>
                    )}
                </div>

                {/* Input Form */}
                <form onSubmit={handleSendMessage} className="p-4 bg-slate-950 border-t border-slate-800 flex gap-3">
                    <input
                        type="text"
                        value={inputQuery}
                        onChange={(e) => setInputQuery(e.target.value)}
                        placeholder="Tanyakan analisis, misal: 'Bagaimana jika main di tempat netral?'"
                        className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-blue-500"
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="bg-blue-600 hover:bg-blue-500 text-white px-5 rounded-xl transition-all flex items-center justify-center cursor-pointer disabled:opacity-50 shadow-lg shadow-blue-600/20"
                    >
                        <Send size={18} />
                    </button>
                </form>

            </div>
        </div>
    );
}