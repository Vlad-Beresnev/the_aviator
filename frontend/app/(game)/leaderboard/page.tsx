'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import type { Score } from '@/lib/api';

export default function LeaderboardPage() {
  const [scores, setScores] = useState<Score[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchScores = async () => {
    try {
      const data = await api.getScores();
      setScores(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scores');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchScores();
    const interval = setInterval(fetchScores, 60000);
    return () => clearInterval(interval);
  }, []);

  return (
    <main className="p-8 max-w-3xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Leaderboard</h1>
        <button
          onClick={fetchScores}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {!loading && !error && (
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b">
              <th className="text-left py-2 pr-4">Rank</th>
              <th className="text-left py-2 pr-4">Player</th>
              <th className="text-left py-2 pr-4">Money</th>
              <th className="text-left py-2 pr-4">Awareness</th>
              <th className="text-left py-2">Last Active</th>
            </tr>
          </thead>
          <tbody>
            {scores.map((score, i) => (
              <tr key={score.name} className="border-b">
                <td className="py-2 pr-4">{i + 1}</td>
                <td className="py-2 pr-4">{score.name}</td>
                <td className="py-2 pr-4">${score.money.toLocaleString()}</td>
                <td className="py-2 pr-4">{score.global_awareness}</td>
                <td className="py-2">{new Date(score.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </main>
  );
}
