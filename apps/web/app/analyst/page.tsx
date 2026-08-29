'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { teams, getTeamLogo } from '@/lib/teams';
import Logo from '@/components/Logo';
import TeamSelect from '@/components/TeamSelect';
import { ArrowUp, Sparkles, Minus, Plus, RotateCcw } from 'lucide-react';

interface GroundTruth {
    home_team: string;
    away_team: string;
    home_win_prob: number;
    away_win_prob: number;
    draw_prob: number;
    top_factor: string;
}

interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    intent?: string;
    tools_called?: string[];
    ground_truth?: GroundTruth | null;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

// Efek ketik halus untuk jawaban bot — hanya jalan sekali saat pesan baru muncul,
// pesan lama tidak diketik ulang karena komponennya tidak remount.
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
        <p className="whitespace-pre-line leading-relaxed">
            {displayed}
            {displayed.length < text.length && <span className="ml-0.5 animate-pulse text-blue-400">▍</span>}
        </p>
    );
}

function greeting(home: string, away: string) {
    return `Halo! Saya ChampIntel AI Agent. Saya siap menganalisis duel ${home} vs ${away} berbasis orkestrasi XGBoost, SHAP Explainability, dan Qwen LLM. Pilih pertanyaan cepat di bawah, atau ajukan pertanyaan taktis bebas.`;
}

export default function AnalystPage() {
    const [homeTeam, setHomeTeam] = useState('Real Madrid');
    const [awayTeam, setAwayTeam] = useState('Bayern Munich');
    const [matchLeg, setMatchLeg] = useState(1);
    const [homeLeg1Score, setHomeLeg1Score] = useState(0);
    const [awayLeg1Score, setAwayLeg1Score] = useState(0);

    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            role: 'assistant',
            content: greeting('Real Madrid', 'Bayern Munich'),
            tools_called: ['Tool: Team Intelligence DB', 'Tool: XGBoost Predictor'],
        },
    ]);
    const [inputQuery, setInputQuery] = useState('');
    const [loading, setLoading] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    const hasUserChatted = messages.some((m) => m.role === 'user');

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    const quickQuestions = [
        `Kelemahan utama ${awayTeam}`,
        `Strategi bertahan terbaik untuk ${awayTeam}`,
        'Duel kunci perebutan lini tengah',
        'Simulasikan kalau kedua tim main agresif',
        'Analisis dampak selisih True Elo',
    ];

    const handleResetChat = () => {
        setMessages([
            {
                role: 'assistant',
                content: `Sesi percakapan di-reset. Siap menganalisis skenario baru untuk ${homeTeam} vs ${awayTeam} (Leg ${matchLeg}).`,
                tools_called: ['Tool: System Memory Reset'],
            },
        ]);
    };

    const sendQuery = async (text: string) => {
        if (!text.trim() || loading) return;

        const userMsg: ChatMessage = { role: 'user', content: text };
        const updatedHistory = [...messages, userMsg];
        setMessages(updatedHistory);
        setInputQuery('');
        setLoading(true);

        try {
            const res = await fetch(`${API_BASE_URL}/agent/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    home_team: homeTeam,
                    away_team: awayTeam,
                    match_leg: matchLeg,
                    home_leg1_score: matchLeg === 2 ? homeLeg1Score : 0,
                    away_leg1_score: matchLeg === 2 ? awayLeg1Score : 0,
                    // Kirim dua nama field sekaligus (query & current_query) supaya tetap
                    // kompatibel baik dengan backend versi lama maupun yang baru.
                    query: text,
                    current_query: text,
                    chat_history: updatedHistory.slice(-4).map((m) => ({ role: m.role, content: m.content })),
                }),
            });

            if (!res.ok) throw new Error('Gagal menghubungi Gateway');

            const data = await res.json();
            setMessages((prev) => [
                ...prev,
                {
                    role: 'assistant',
                    content: data.response || 'Analisis berhasil dibuat.',
                    intent: data.intent,
                    tools_called: data.tools_called || [],
                    ground_truth: data.ground_truth || null,
                },
            ]);
        } catch (err) {
            setMessages((prev) => [
                ...prev,
                { role: 'assistant', content: 'Maaf, terjadi kendala saat menghubungi Agent Orchestrator melalui Gateway Go.' },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
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
                    <h1 className="flex flex-wrap items-center gap-2 text-2xl font-bold tracking-tight text-white md:text-3xl">
                        <Sparkles className="text-blue-400" size={24} />
                        ChampIntel AI Agent
                        <span className="rounded-md border border-blue-500/30 bg-blue-500/20 px-2 py-0.5 font-mono text-[10px] uppercase text-blue-400">
                            OpenClaw Architecture
                        </span>
                    </h1>
                    <p className="mt-1 text-sm text-slate-400">
                        Orkestrator taktikal otonom berbasis multi-tool calling: XGBoost, SHAP, True Elo, &amp; Qwen 2.5.
                    </p>
                </div>
            </div>

            {/* Konfigurasi Klub & Leg */}
            <div className="space-y-4 rounded-2xl border border-slate-800 bg-slate-900 p-4 shadow-xl">
                <div className="flex flex-wrap items-end gap-3">
                    <div className="min-w-[180px] flex-1">
                        <TeamSelect label="Tim Kandang" value={homeTeam} onChange={setHomeTeam} excludeTeam={awayTeam} />
                    </div>
                    <span className="mb-2.5 text-xs font-bold text-slate-500">VS</span>
                    <div className="min-w-[180px] flex-1">
                        <TeamSelect label="Tim Tandang" value={awayTeam} onChange={setAwayTeam} excludeTeam={homeTeam} />
                    </div>
                    <button
                        onClick={handleResetChat}
                        title="Reset Obrolan"
                        className="mb-0.5 flex h-9 w-9 items-center justify-center rounded-lg border border-slate-800 bg-slate-950 text-slate-400 transition-colors hover:border-amber-500/40 hover:text-amber-400"
                    >
                        <RotateCcw size={14} />
                    </button>
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
                                    onClick={() => setHomeLeg1Score(Math.max(0, homeLeg1Score - 1))}
                                    className="flex h-6 w-6 items-center justify-center rounded-md border border-slate-800 bg-slate-950 text-slate-400 hover:text-blue-400"
                                >
                                    <Minus size={11} />
                                </button>
                                <span className="w-5 text-center font-bold text-white">{homeLeg1Score}</span>
                                <button
                                    type="button"
                                    onClick={() => setHomeLeg1Score(homeLeg1Score + 1)}
                                    className="flex h-6 w-6 items-center justify-center rounded-md border border-slate-800 bg-slate-950 text-slate-400 hover:text-blue-400"
                                >
                                    <Plus size={11} />
                                </button>
                            </div>
                            <span className="text-slate-700">—</span>
                            <div className="flex items-center gap-1.5">
                                <button
                                    type="button"
                                    onClick={() => setAwayLeg1Score(Math.max(0, awayLeg1Score - 1))}
                                    className="flex h-6 w-6 items-center justify-center rounded-md border border-slate-800 bg-slate-950 text-slate-400 hover:text-blue-400"
                                >
                                    <Minus size={11} />
                                </button>
                                <span className="w-5 text-center font-bold text-white">{awayLeg1Score}</span>
                                <button
                                    type="button"
                                    onClick={() => setAwayLeg1Score(awayLeg1Score + 1)}
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
            <div className="flex h-[560px] flex-col overflow-hidden rounded-3xl border border-slate-800 bg-slate-900 shadow-xl">
                <div className="flex-1 space-y-4 overflow-y-auto p-6">
                    {/* Pertanyaan cepat — di atas, sebelum sapaan, hilang setelah chat dimulai */}
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

                    <AnimatePresence initial={false}>
                        {messages.map((m, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`flex items-start gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}
                            >
                                <div
                                    className={`flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full ${m.role === 'user' ? 'bg-blue-600 text-white' : 'border border-indigo-500/30 bg-indigo-600/30'
                                        }`}
                                >
                                    {m.role === 'user' ? (
                                        <span className="text-xs font-bold">U</span>
                                    ) : (
                                        <Logo src="/icon.png" alt="ChampIntel" size={32} />
                                    )}
                                </div>

                                <div
                                    className={`max-w-[85%] space-y-2.5 rounded-2xl p-4 text-sm shadow-md ${m.role === 'user'
                                            ? 'rounded-tr-none bg-blue-600 text-white'
                                            : 'rounded-tl-none border border-slate-800 bg-slate-950 text-slate-200'
                                        }`}
                                >
                                    {/* Badge tools yang dipanggil — bukti nyata agent orchestration */}
                                    {m.tools_called && m.tools_called.length > 0 && (
                                        <div className="flex flex-wrap gap-1.5 border-b border-slate-800/60 pb-2">
                                            {m.tools_called.map((tool, tIdx) => (
                                                <span
                                                    key={tIdx}
                                                    className="rounded-md border border-blue-800/40 bg-blue-950/50 px-2 py-0.5 font-mono text-[9px] text-blue-300"
                                                >
                                                    ⚙️ {tool}
                                                </span>
                                            ))}
                                        </div>
                                    )}

                                    {m.role === 'assistant' ? (
                                        <TypewriterText text={m.content} />
                                    ) : (
                                        <p className="whitespace-pre-line">{m.content}</p>
                                    )}

                                    {/* Kartu ground truth: intent + angka XGBoost mentah */}
                                    {m.ground_truth && (
                                        <div className="flex flex-wrap items-center gap-2 border-t border-slate-800/60 pt-2 text-[10px]">
                                            <span className="rounded-md border border-emerald-500/30 bg-emerald-950/40 px-2 py-0.5 font-mono text-emerald-400">
                                                🎯 Intent: {m.intent}
                                            </span>
                                            <span className="font-mono text-slate-400">
                                                📊 {m.ground_truth.home_team} ({(m.ground_truth.home_win_prob * 100).toFixed(0)}%) vs{' '}
                                                {m.ground_truth.away_team} ({(m.ground_truth.away_win_prob * 100).toFixed(0)}%)
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {loading && (
                        <div className="flex items-start gap-3">
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-full border border-indigo-500/30 bg-indigo-600/30">
                                <Logo src="/icon.png" alt="ChampIntel" size={32} />
                            </div>
                            <div className="flex items-center gap-3 rounded-2xl rounded-tl-none border border-slate-800 bg-slate-950 p-4">
                                <span className="flex gap-1.5">
                                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-500 [animation-delay:-0.3s]" />
                                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-500 [animation-delay:-0.15s]" />
                                    <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-500" />
                                </span>
                                <span className="font-mono text-[11px] text-blue-400">Agent sedang menjalankan tools & menghitung...</span>
                            </div>
                        </div>
                    )}
                    <div ref={bottomRef} />
                </div>

                {/* Input Form */}
                <form onSubmit={handleSubmit} className="flex gap-3 border-t border-slate-800 bg-slate-950 p-4">
                    <input
                        type="text"
                        value={inputQuery}
                        onChange={(e) => setInputQuery(e.target.value)}
                        placeholder="Tanyakan analisis taktik lanjutan (misal: 'Bagaimana cara membongkar pertahanan lawan?')..."
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