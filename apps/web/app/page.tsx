'use client';

import React, { useState } from 'react';
import { fetchPrediction } from '@/lib/api';
import { PredictionResponse } from '@/lib/types';
import MatchHero from '@/components/MatchHero';
import TeamPicker from '@/components/TeamPicker';
import MatchConfigForm from '@/components/MatchConfigForm';
import SimulationPanel from '@/components/SimulationPanel';
import PredictionResult from '@/components/PredictionResult';

type Selecting = 'home' | 'away';

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
      // Hanya mengirim identitas tim dan skor leg, statistik dihitung otomatis oleh AI Service
      const data = await fetchPrediction({
        home_team: homeTeam,
        away_team: awayTeam,
        match_leg: Number(matchLeg),
        home_leg1_score: matchLeg === 2 ? Number(homeLeg1) : null,
        away_leg1_score: matchLeg === 2 ? Number(awayLeg1) : null,
      });
      setResult(data);

      const newHistoryItem = {
        id: Date.now(),
        date: new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }),
        homeTeam,
        awayTeam,
        matchLeg,
        result: data,
      };
      const existing = JSON.parse(localStorage.getItem('ucl_predictions') || '[]');
      localStorage.setItem('ucl_predictions', JSON.stringify([newHistoryItem, ...existing]));

    } catch (err: any) {
      setError(err.message || 'Terjadi kesalahan sistem.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <MatchHero />

      <TeamPicker
        homeTeam={homeTeam}
        awayTeam={awayTeam}
        selecting={selecting}
        setSelecting={setSelecting}
        swapTeams={swapTeams}
        handlePick={handlePick}
      />

      <MatchConfigForm
        homeTeam={homeTeam}
        awayTeam={awayTeam}
        matchLeg={matchLeg}
        setMatchLeg={setMatchLeg}
        homeLeg1={homeLeg1}
        setHomeLeg1={setHomeLeg1}
        awayLeg1={awayLeg1}
        setAwayLeg1={setAwayLeg1}
        loading={loading}
        error={error}
        onPredict={handlePredict}
      />

      <PredictionResult
        homeTeam={homeTeam}
        awayTeam={awayTeam}
        result={result}
      />

      {result && (
        <SimulationPanel
          homeTeam={homeTeam}
          awayTeam={awayTeam}
          matchLeg={matchLeg}
          homeLeg1Score={matchLeg === 2 ? Number(homeLeg1) : null}
          awayLeg1Score={matchLeg === 2 ? Number(awayLeg1) : null}
        />
      )}
    </div>
  );
}