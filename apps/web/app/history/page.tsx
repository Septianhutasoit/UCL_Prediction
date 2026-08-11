'use client';

import React, { useEffect, useState } from 'react';
import HistoryItem from '@/components/HistoryItem';

export default function HistoryPage() {
    const [history, setHistory] = useState<any[]>([]);

    // Ambil riwayat dari localStorage saat halaman dimuat
    useEffect(() => {
        const saved = localStorage.getItem('ucl_predictions');
        if (saved) {
            try {
                setHistory(JSON.parse(saved));
            } catch (e) {
                console.error("Gagal memparsing riwayat", e);
            }
        }
    }, []);

    // Hapus satu item riwayat
    const handleDelete = (id: number) => {
        const updated = history.filter((item) => item.id !== id);
        setHistory(updated);
        localStorage.setItem('ucl_predictions', JSON.stringify(updated));
    };

    // Hapus semua riwayat
    const handleClearAll = () => {
        setHistory([]);
        localStorage.removeItem('ucl_predictions');
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8">

            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white">Prediction History</h1>
                    <p className="text-slate-400 mt-1">
                        Daftar riwayat prediksi pertandingan yang pernah kamu lakukan sebelumnya.
                    </p>
                </div>
                {history.length > 0 && (
                    <button
                        onClick={handleClearAll}
                        className="bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-500/30 px-4 py-2 rounded-xl text-xs font-semibold transition-colors cursor-pointer"
                    >
                        Hapus Semua Riwayat
                    </button>
                )}
            </div>

            {/* Daftar Riwayat atau State Kosong */}
            {history.length === 0 ? (
                <div className="bg-slate-900/50 border border-slate-800/60 border-dashed rounded-3xl p-16 text-center text-slate-500 space-y-3">
                    <span className="text-4xl">📜</span>
                    <p className="text-sm font-medium text-slate-400">Belum ada riwayat prediksi yang tersimpan.</p>
                    <p className="text-xs text-slate-600">Lakukan prediksi baru di halaman Match Predictor agar tersimpan di sini secara otomatis!</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {history.map((item) => (
                        <HistoryItem key={item.id} item={item} onDelete={handleDelete} />
                    ))}
                </div>
            )}

        </div>
    );
}