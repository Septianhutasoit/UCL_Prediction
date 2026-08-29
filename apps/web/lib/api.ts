import { PredictionRequest, PredictionResponse } from './types';

// Alamat Backend Go + Gin
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api/v1';

export async function fetchPrediction(data: PredictionRequest): Promise<PredictionResponse> {
    const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        throw new Error('Gagal terhubung ke Backend Go atau AI Service');
    }

    return response.json();
}

export async function fetchHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/history`, {
            cache: 'no-store'
        });

        if (!response.ok) {
            // Fallback ke localStorage jika gateway belum ada data
            if (typeof window !== 'undefined') {
                const localData = localStorage.getItem('champintel_history');
                return localData ? JSON.parse(localData) : [];
            }
            return [];
        }
        return await response.json();
    } catch (error) {
        // Fallback aman jika server offline
        if (typeof window !== 'undefined') {
            const localData = localStorage.getItem('champintel_history');
            return localData ? JSON.parse(localData) : [];
        }
        return [];
    }
}