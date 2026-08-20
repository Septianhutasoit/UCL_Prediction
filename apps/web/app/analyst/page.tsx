'use client';

import React, { useState, useEffect } from 'react';
import { teams, getTeamLogo } from '@/lib/teams';
import Logo from '@/components/Logo';
import { ArrowUp, User, Sparkles, Minus, Plus } from 'lucide-react';

type ChatMessage = { role: 'user' | 'assistant'; content: string };

// Efek ketik halus untuk jawaban bot — hanya jalan sekali saat pesan baru muncul,
// pesan lama tidak akan diketik ulang karena komponennya tidak remount.
function TypewriterText({ text, speed = 16 }: { text: string; speed?: number }) {
    const [displayed, setDisplayed] = useState('');

    useEffect(() => {
        setDisplayed('');
        let i = 0;
        const interval = setInterval(() => {
            i += 2;
            setDisplayed(text.slice(0, i));
            if (i >= text.length) clearInterval(interval);
        }, speed);
        return () => clearInterval(interval);
    }, [text]);

    return (
        <p className="whitespace-pre-line">
            {displayed}
            {displayed.length < text.length && <span className="ml-0.5 animate-pulse text-blue-400">▍</span>}
        </p>
    );
}

const quickQuestions = [
    'Analisis taktik laga ini secara mendalam',
    'Bagaimana jika main di tempat netral?',
    'Simulasikan kalau kedua tim main agresif',
    'Siapa favorit lolos di Leg 2?',
];

export default function AnalystPage() {
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: 'assistant',
            content:
                'Halo! Saya ChampIntel Analyst Agent. Pilih dua klub & leg di bawah, lalu tanyakan analisis taktik, prediksi, atau jalankan simulasi skenario (misal: "Bagaimana jika main di tempat netral?").',
        },
    ]);
    const [inputQuery, setInputQuery] = useState('');
    const [homeTeam, setHomeTeam] = useState('Real Madrid');
    const [awayTeam, setAwayTeam] = useState('Bayern Munich');
    const [matchLeg, setMatchLeg] = useState(2);
    const [homeLeg1, setHomeLeg1] = useState(1);
    const [awayLeg1, setAwayLeg1] = useState(2);
    const [loading, setLoading] = useState(false);

    const hasUserChatted = messages.some((m) => m.role === 'user');

    const sendQuery = async (text: string) => {
        if (!text.trim() || loading) return;

        setInputQuery('');
        setMessages((prev) => [...prev, { role: 'user', content: text }]);
        setLoading(true);

        try {
            const res = await fetch('http://localhost:8000/agent/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query: text,
                    home_team: homeTeam,
                    away_team: awayTeam,
                    match_leg: Number(matchLeg),
                    home_leg1_score: Number(homeLeg1),
                    away_leg1_score: Number(awayLeg1),
                }),
            });

            if (!res.ok) throw new Error('Gagal terhubung ke AI Agent');

            const data = await res.json();
            setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
        } catch (err) {
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: 'Maaf, terjadi kesalahan saat menghubungi AI Agent. Pastikan FastAPI dan Backend menyala.' },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleSendMessage = (e: React.FormEvent) => {
        e.preventDefault();
        sendQuery(inputQuery);
    };

    return (
        <div className="mx-auto max-w-4xl space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <div className="relative h-14 w-14 shrink-0 overflow-hidden rounded-2xl shadow-lg shadow-blue-500/20">
                    <Logo src="/icon.png" alt="UEFA Champions League" size={56} className="h-full w-full" />
                </div>
                <div>
                    <h1 className="flex items-center gap-2 text-3xl font-bold tracking-tight text-white">
                        <Sparkles className="text-blue-400" size={26} /> ChampIntel Analyst Agent
                    </h1>
                    <p className="mt-1 text-sm text-slate-400">
                        Asisten AI interaktif berbasis agent yang siap menjawab pertanyaan taktis seputar laga UEFA Champions
                        League.
                    </p>
                </div>
            </div>

            {/* Konfigurasi Klub & Leg untuk Chat */}
            <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900 p-4 shadow-xl">
                <div className="flex flex-wrap items-center gap-3">
                    <span className="text-xs font-semibold text-slate-400">Klub Fokus Laga:</span>

                    <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950 px-3 py-1.5">
                        <Logo src={getTeamLogo(homeTeam)} alt={homeTeam} size={20} />
                        <select
                            value={homeTeam}
                            onChange={(e) => setHomeTeam(e.target.value)}
                            className="cursor-pointer bg-transparent text-xs text-white focus:outline-none"
                        >
                            {teams.map((t) => (
                                <option key={t.name} value={t.name} className="bg-slate-900 text-white">
                                    {t.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <span className="text-xs font-bold text-slate-500">VS</span>

                    <div className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-950 px-3 py-1.5">
                        <Logo src={getTeamLogo(awayTeam)} alt={awayTeam} size={20} />
                        <select
                            value={awayTeam}
                            onChange={(e) => setAwayTeam(e.target.value)}
                            className="cursor-pointer bg-transparent text-xs text-white focus:outline-none"
                        >
                            {teams.map((t) => (
                                <option key={t.name} value={t.name} className="bg-slate-900 text-white">
                                    {t.name}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                <div className="flex flex-wrap items-center gap-3 border-t border-slate-800 pt-4">
                    <span className="text-xs font-semibold text-slate-400">Konteks Laga:</span>

                    <div className="inline-flex rounded-lg border border-slate-800 bg-slate-950 p-1">
                        <button
                            type="button"
                            onClick={() => setMatchLeg(1)}
                            className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-all ${matchLeg === 1 ? 'bg-blue-600 text-white shadow shadow-blue-600/30' : 'text-slate-400 hover:text-slate-200'
                                }`}
                        >
                            Leg 1
                        </button>
                        <button
                            type="button"
                            onClick={() => setMatchLeg(2)}
                            className={`rounded-md px-3 py-1.5 text-xs font-semibold transition-all ${matchLeg === 2 ? 'bg-blue-600 text-white shadow shadow-blue-600/30' : 'text-slate-400 hover:text-slate-200'
                                }`}
                        >
                            Leg 2
                        </button>
                    </div>

                    {matchLeg === 2 && (
                        <div className="flex items-center gap-4 text-xs text-slate-400">
                            <span className="text-slate-600">Skor Leg 1:</span>

                            <div className="flex items-center gap-1.5">
                                <span className="max-w-[90px] truncate">{homeTeam}</span>
                                <button
                                    type="button"
                                    onClick={() => setHomeLeg1(Math.max(0, homeLeg1 - 1))}
                                    className="flex h-6 w-6 items-center justify-center rounded-md border border-slate-800 bg-slate-950 text-slate-400 hover:text-blue-400"
                                >
                                    <Minus size={11} />
                                </button>
                                <span className="w-5 text-center font-bold text-white">{homeLeg1}</span>
                                <button
                                    type="button"
                                    onClick={() => setHomeLeg1(homeLeg1 + 1)}
                                    className="flex h-6 w-6 items-center justify-center rounded-md border border-slate-800 bg-slate-950 text-slate-400 hover:text-blue-400"
                                >
                                    <Plus size={11} />
                                </button>
                            </div>

                            <span className="text-slate-700">—</span>

                            <div className="flex items-center gap-1.5">
                                <button
                                    type="button"
                                    onClick={() => setAwayLeg1(Math.max(0, awayLeg1 - 1))}
                                    className="flex h-6 w-6 items-center justify-center rounded-md border border-slate-800 bg-slate-950 text-slate-400 hover:text-blue-400"
                                >
                                    <Minus size={11} />
                                </button>
                                <span className="w-5 text-center font-bold text-white">{awayLeg1}</span>
                                <button
                                    type="button"
                                    onClick={() => setAwayLeg1(awayLeg1 + 1)}
                                    className="flex h-6 w-6 items-center justify-center rounded-md border border-slate-800 bg-slate-950 text-slate-400 hover:text-blue-400"
                                >
                                    <Plus size={11} />
                                </button>
                                <span className="max-w-[90px] truncate">{awayTeam}</span>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Chat Container */}
            <div className="flex h-[550px] flex-col overflow-hidden rounded-3xl border border-slate-800 bg-slate-900 shadow-xl">
                <div className="flex-1 space-y-4 overflow-y-auto p-6">
                    {/* Pertanyaan cepat — sekarang di paling atas, sebelum bubble sapaan */}
                    {!hasUserChatted && (
                        <div className="flex flex-wrap gap-2">
                            {quickQuestions.map((q) => (
                                <button
                                    key={q}
                                    onClick={() => sendQuery(q)}
                                    disabled={loading}
                                    className="rounded-full border border-slate-800 bg-slate-900 px-3.5 py-2 text-xs text-slate-300 transition-all hover:border-blue-500/40 hover:bg-blue-500/10 hover:text-blue-300 disabled:opacity-50"
                                >
                                    {q}
                                </button>
                            ))}
                        </div>
                    )}

                    {messages.map((msg, idx) => (
                        <div key={idx} className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                            <div
                                className={`flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'border border-indigo-500/30 bg-indigo-600/30'
                                    }`}
                            >
                                {msg.role === 'user' ? <User size={16} /> : <Logo src="/icon.png" alt="ChampIntel" size={32} />}
                            </div>
                            <div
                                className={`max-w-[85%] rounded-2xl p-4 text-sm leading-relaxed ${msg.role === 'user'
                                        ? 'rounded-tr-none bg-blue-600 text-white'
                                        : 'rounded-tl-none border border-slate-800 bg-slate-950 text-slate-200 shadow-md'
                                    }`}
                            >
                                {msg.role === 'assistant' ? (
                                    <TypewriterText text={msg.content} />
                                ) : (
                                    <p className="whitespace-pre-line">{msg.content}</p>
                                )}
                            </div>
                        </div>
                    ))}

                    {loading && (
                        <div className="flex items-start gap-3">
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full border border-indigo-500/30 bg-indigo-600/30">
                                <Logo src="/icon.png" alt="ChampIntel" size={32} />
                            </div>
                            <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-none border border-slate-800 bg-slate-950 p-4">
                                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-500 [animation-delay:-0.3s]" />
                                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-500 [animation-delay:-0.15s]" />
                                <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-500" />
                            </div>
                        </div>
                    )}
                </div>

                {/* Input Form */}
                <form onSubmit={handleSendMessage} className="flex gap-3 border-t border-slate-800 bg-slate-950 p-4">
                    <input
                        type="text"
                        value={inputQuery}
                        onChange={(e) => setInputQuery(e.target.value)}
                        placeholder="Tanyakan analisis, misal: 'Bagaimana jika main di tempat netral?'"
                        className="flex-1 rounded-xl border border-slate-800 bg-slate-900 px-4 py-3 text-sm text-white focus:border-blue-500 focus:outline-none"
                    />
                    <button
                        type="submit"
                        disabled={loading}
                        className="flex h-11 w-11 shrink-0 cursor-pointer items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-600/20 transition-all hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-70"
                    >
                        {loading ? <span className="h-3.5 w-3.5 rounded-md bg-white" /> : <ArrowUp size={20} />}
                    </button>
                </form>
            </div>
        </div>
    );
}