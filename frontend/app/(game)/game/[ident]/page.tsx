'use client';

import dynamic from 'next/dynamic';
import { useParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { api, Airport } from '@/lib/api';
import { MAX_BATTERY } from '@/components/game/constants';
import ResultOverlay from '@/components/game/ResultOverlay';

const PhaserGameDynamic = dynamic(
  () => import('@/components/game/PhaserGame'),
  { ssr: false }
);

export default function GamePage() {
  const params = useParams<{ ident: string }>();
  const ident = params.ident;

  const [airport, setAirport] = useState<Airport | null>(null);
  const [battery, setBattery] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [result, setResult] = useState<{ victory: boolean } | null>(null);

  useEffect(() => {
    const load = async () => {
      await api.startGame();
      const [airportData, gameState] = await Promise.all([
        api.getAirport(ident),
        api.getGameState(),
      ]);
      const computed = Math.max(0, Math.min(MAX_BATTERY, MAX_BATTERY - gameState.battery_used));
      setAirport(airportData);
      setBattery(computed);
      setLoading(false);
    };

    load();
  }, [ident]);

  const handleComplete = async (res: { victory: boolean; battery: number }) => {
    if (res.victory) {
      try {
        await api.completeLevel(ident);
      } catch {
        // level already completed or network error — still show overlay
      }
    }
    setResult({ victory: res.victory });
  };

  if (loading || !airport || battery === null) {
    return (
      <main style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
        <p>Loading...</p>
      </main>
    );
  }

  return (
    <main>
      <PhaserGameDynamic
        difficulty={airport.difficulty}
        level={airport.level}
        battery={battery}
        onComplete={handleComplete}
      />
      {result !== null && (
        <ResultOverlay
          victory={result.victory}
          airportName={airport.name}
          earnedMoney={airport.speaker_fee}
          onBack={() => { window.location.href = '/map'; }}
          onRetry={() => window.location.reload()}
        />
      )}
    </main>
  );
}
