'use client';

import React, { useEffect, useState } from 'react';
import HistoryItem from '@/components/HistoryItem';
import { fetchHistory } from '@/lib/api';

export default function HistoryPage() {
    const [history, setHistory] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);

    // Ambil riwayat langsung dari database Supabase via Backend Go
    useEffect(() => {
        async function loadHistory() {
            try {
                const data = await fetchHistory();
                if (data) {
                    // Format ulang data dari database agar sesuai dengan komponen HistoryItem
                    const formatted = data.map((item: any) => ({
                        id: item.id,
                        date: new Date(item.date).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }),
                        homeTeam: item.home_team,
                        awayTeam: item.away_team,
                        matchLeg: item.match_leg,
                        result: item.result,
                    }));
                    setHistory(formatted);
                }
            } catch (err) {
                console.error('Gagal memuat riwayat:', err);
            } finally {
                setLoading(false);
            }
        }
        loadHistory();
    }, []);

    // Hapus item (opsional, bisa di-skip atau dihubungkan ke backend delete jika mau)
    const handleDelete = (id: number) => {
        const updated = history.filter((item) => item.id !== id);
        setHistory(updated);
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8">

            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-white">Prediction History (Cloud DB)</h1>
                    <p className="text-slate-400 mt-1">
                        Daftar riwayat prediksi pertandingan yang ditarik langsung secara permanen dari database Supabase.
                    </p>
                </div>
            </div>

            {/* Loading state */}
            {loading ? (
                <div className="py-16 text-center text-slate-400 animate-pulse font-medium">
                    🔄 Memuat riwayat dari database Supabase...
                </div>
            ) : history.length === 0 ? (
                <div className="bg-slate-900/50 border border-slate-800/60 border-dashed rounded-3xl p-16 text-center text-slate-500 space-y-3">
                    <span className="text-4xl">📜</span>
                    <p className="text-sm font-medium text-slate-400">Belum ada riwayat prediksi di database.</p>
                    <p className="text-xs text-slate-600">Lakukan prediksi baru di halaman Match Predictor agar tersimpan di Supabase!</p>
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