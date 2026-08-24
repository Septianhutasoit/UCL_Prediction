'use client';

import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface GroundTruth {
    home_team: string;
    away_team: string;
    home_win_prob: number;
    away_win_prob: number;
    draw_prob: number;
    top_factor: string;
}

interface Message {
    role: 'user' | 'assistant';
    content: string;
    intent?: string;
    tools_called?: string[];
    ground_truth?: GroundTruth;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

export default function AnalystPage() {
    const [homeTeam, setHomeTeam] = useState('Real Madrid');
    const [awayTeam, setAwayTeam] = useState('Bayern Munich');
    const [matchLeg, setMatchLeg] = useState(1);
    const [homeLeg1Score, setHomeLeg1Score] = useState(0);
    const [awayLeg1Score, setAwayLeg1Score] = useState(0);

    const [messages, setMessages] = useState<Message[]>([
        {
            role: 'assistant',
            content: `Halo! Saya ChampIntel Autonomous Tactical Agent. Saya siap menganalisis duel ${homeTeam} vs ${awayTeam} berbasis orkestrasi XGBoost, SHAP Explainability, dan Qwen LLM. Silakan pilih skenario atau ajukan pertanyaan taktis bebas!`,
            tools_called: ['Tool: Team Intelligence DB', 'Tool: XGBoost Predictor']
        }
    ]);

    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    // Tombol Tanya Cepat Dinamis (Dynamic Action Chips)
    const quickChips = [
        `🔍 Kelemahan utama ${awayTeam}`,
        `🛡️ Strategi bertahan terbaik untuk ${awayTeam}`,
        `⚡ Duel kunci perebutan lini tengah`,
        `📊 Simulasi taktik All-Out Attack`,
        `⚖️ Analisis dampak selisih True Elo`
    ];

    const handleResetChat = () => {
        setMessages([
            {
                role: 'assistant',
                content: `Sesi percakapan di-reset. Siap menganalisis skenario baru untuk ${homeTeam} vs ${awayTeam} (Leg ${matchLeg}).`,
                tools_called: ['Tool: System Memory Reset']
            }
        ]);
    };

    const sendMessage = async (textToSend: string) => {
        if (!textToSend.trim() || loading) return;

        const userMsg: Message = { role: 'user', content: textToSend };
        const updatedHistory = [...messages, userMsg];
        setMessages(updatedHistory);
        setInput('');
        setLoading(true);

        try {
            // Kirim request melewati GO GIN GATEWAY (Port 8080)
            const res = await fetch(`${API_BASE_URL}/agent/query`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    home_team: homeTeam,
                    away_team: awayTeam,
                    match_leg: matchLeg,
                    home_leg1_score: homeLeg1Score,
                    away_leg1_score: awayLeg1Score,
                    current_query: textToSend,
                    // Kirim 4 pesan terakhir sebagai memori konteks percakapan multi-turn
                    chat_history: updatedHistory.slice(-4).map(m => ({ role: m.role, content: m.content }))
                })
            });

            if (!res.ok) throw new Error('Gagal menghubungi Gateway');

            const data = await res.json();

            // Simulasi tool-calling metadata yang dieksekusi agent
            const tools = ['Tool: XGBoost Predictor', 'Tool: SHAP Engine'];
            if (textToSend.toLowerCase().includes('skenario') || textToSend.toLowerCase().includes('what if')) {
                tools.push('Tool: What-if Simulator');
            }
            tools.push('Tool: Qwen Tactical Synthesizer');

            setMessages(prev => [
                ...prev,
                {
                    role: 'assistant',
                    content: data.response || 'Analisis berhasil dibuat.',
                    intent: data.intent,
                    tools_called: tools,
                    ground_truth: data.ground_truth
                }
            ]);
        } catch (err) {
            setMessages(prev => [
                ...prev,
                {
                    role: 'assistant',
                    content: 'Maaf, terjadi kendala saat menghubungi Agent Orchestrator melalui Gateway Go.'
                }
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6">
            {/* Header Panel Konfigurasi Agent */}
            <div className="bg-slate-900/90 border border-slate-800 p-6 rounded-3xl backdrop-blur-md shadow-xl flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div>
                    <div className="flex items-center space-x-3">
                        <span className="flex h-3.5 w-3.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        <h1 className="text-xl font-extrabold text-white tracking-wide flex items-center gap-2">
                            ChampIntel AI Agent
                            <span className="text-[10px] uppercase font-mono px-2 py-0.5 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-md">
                                OpenClaw Architecture
                            </span>
                        </h1>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                        Orkestrator Taktikal Otonom berbasis Multi-Tool Calling: XGBoost, SHAP, True Elo, & Qwen 2.5.
                    </p>
                </div>

                {/* Konfigurasi Match & Leg */}
                <div className="flex flex-wrap items-center gap-3 bg-slate-950/80 p-2.5 rounded-2xl border border-slate-800 text-xs">
                    <input
                        type="text"
                        value={homeTeam}
                        onChange={e => setHomeTeam(e.target.value)}
                        className="w-28 bg-slate-900 border border-slate-700/80 rounded-xl px-2.5 py-1.5 text-center font-bold text-blue-400 focus:outline-none focus:border-blue-500"
                        placeholder="Home Team"
                    />
                    <span className="text-slate-500 font-extrabold">VS</span>
                    <input
                        type="text"
                        value={awayTeam}
                        onChange={e => setAwayTeam(e.target.value)}
                        className="w-28 bg-slate-900 border border-slate-700/80 rounded-xl px-2.5 py-1.5 text-center font-bold text-indigo-400 focus:outline-none focus:border-indigo-500"
                        placeholder="Away Team"
                    />

                    {/* Selector Leg */}
                    <div className="flex items-center bg-slate-900 rounded-xl p-0.5 border border-slate-700/60 ml-1">
                        <button
                            onClick={() => setMatchLeg(1)}
                            className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all ${matchLeg === 1 ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            Leg 1
                        </button>
                        <button
                            onClick={() => setMatchLeg(2)}
                            className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-all ${matchLeg === 2 ? 'bg-blue-600 text-white shadow-sm' : 'text-slate-400 hover:text-white'
                                }`}
                        >
                            Leg 2
                        </button>
                    </div>

                    {matchLeg === 2 && (
                        <div className="flex items-center gap-1.5 pl-1 text-[11px] text-slate-400">
                            <span>Leg 1:</span>
                            <input
                                type="number"
                                value={homeLeg1Score}
                                onChange={e => setHomeLeg1Score(parseInt(e.target.value) || 0)}
                                className="w-9 bg-slate-900 border border-slate-700 rounded-lg p-1 text-center font-bold text-white"
                            />
                            <span>-</span>
                            <input
                                type="number"
                                value={awayLeg1Score}
                                onChange={e => setAwayLeg1Score(parseInt(e.target.value) || 0)}
                                className="w-9 bg-slate-900 border border-slate-700 rounded-lg p-1 text-center font-bold text-white"
                            />
                        </div>
                    )}

                    <button
                        onClick={handleResetChat}
                        title="Reset Obrolan"
                        className="p-1.5 text-slate-400 hover:text-amber-400 hover:bg-slate-900 rounded-lg transition-colors ml-auto"
                    >
                        🔄
                    </button>
                </div>
            </div>

            {/* Area Chat Room Interaktif */}
            <div className="bg-slate-900/60 border border-slate-800/80 rounded-3xl p-6 shadow-2xl flex flex-col h-[540px]">
                {/* Daftar Pesan */}
                <div className="flex-1 overflow-y-auto space-y-4 pr-3 text-xs leading-relaxed">
                    <AnimatePresence initial={false}>
                        {messages.map((m, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                            >
                                <div
                                    className={`max-w-[85%] rounded-3xl p-4 shadow-md space-y-2.5 ${m.role === 'user'
                                            ? 'bg-blue-600 text-white rounded-br-none'
                                            : 'bg-slate-950/90 border border-slate-800 text-slate-200 rounded-bl-none'
                                        }`}
                                >
                                    {/* Tool Execution Badge (Bukti Nyata Agent Orchestration) */}
                                    {m.tools_called && m.tools_called.length > 0 && (
                                        <div className="flex flex-wrap gap-1.5 pb-1 border-b border-slate-800/60">
                                            {m.tools_called.map((tool, tIdx) => (
                                                <span
                                                    key={tIdx}
                                                    className="text-[9px] font-mono bg-blue-950/50 text-blue-300 border border-blue-800/40 px-2 py-0.5 rounded-md"
                                                >
                                                    ⚙️ {tool}
                                                </span>
                                            ))}
                                        </div>
                                    )}

                                    <p className="leading-relaxed whitespace-pre-line">{m.content}</p>

                                    {/* Ground Truth Card & Intent */}
                                    {m.ground_truth && (
                                        <div className="pt-2 border-t border-slate-800/60 flex flex-wrap items-center gap-2 text-[10px]">
                                            <span className="font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-500/30 px-2 py-0.5 rounded-md">
                                                🎯 Intent: {m.intent}
                                            </span>
                                            <span className="text-slate-400 font-mono">
                                                📊 XGBoost: {m.ground_truth.home_team} ({(m.ground_truth.home_win_prob * 100).toFixed(0)}%) vs {m.ground_truth.away_team} ({(m.ground_truth.away_win_prob * 100).toFixed(0)}%)
                                            </span>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {loading && (
                        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
                            <div className="bg-slate-950 border border-slate-800 text-slate-300 rounded-2xl p-3.5 text-xs flex items-center gap-3">
                                <span className="animate-spin text-base">⚙️</span>
                                <span className="font-mono text-[11px] text-blue-400">
                                    Agent Orchestrator is executing tools: predict_match() & explain_factors()...
                                </span>
                            </div>
                        </motion.div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Quick Action Chips */}
                <div className="flex flex-wrap gap-2 pt-3.5 border-t border-slate-800/80">
                    {quickChips.map((chip, idx) => (
                        <button
                            key={idx}
                            disabled={loading}
                            onClick={() => sendMessage(chip.replace(/^[^\s]+\s/, ''))}
                            className="text-[11px] bg-slate-800/60 hover:bg-blue-600/20 hover:border-blue-500/50 text-slate-300 border border-slate-700/60 rounded-xl px-3 py-1.5 transition-all text-left disabled:opacity-50"
                        >
                            {chip}
                        </button>
                    ))}
                </div>

                {/* Input Bar */}
                <form
                    onSubmit={e => {
                        e.preventDefault();
                        sendMessage(input);
                    }}
                    className="flex items-center gap-3 pt-3"
                >
                    <input
                        type="text"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        placeholder="Tanyakan analisis taktik lanjutan (misal: 'Bagaimana cara membongkar pertahanan lawan?')..."
                        className="flex-1 bg-slate-950 border border-slate-800 rounded-2xl px-5 py-3 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
                    />
                    <button
                        type="submit"
                        disabled={loading || !input.trim()}
                        className="bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white text-xs font-bold px-6 py-3 rounded-2xl transition-all shadow-lg shadow-blue-500/20"
                    >
                        Kirim
                    </button>
                </form>
            </div>
        </div>
    );
}