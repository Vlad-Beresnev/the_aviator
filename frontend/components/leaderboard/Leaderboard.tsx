'use client';

import { useCallback, useEffect, useState, useSyncExternalStore } from 'react';
import { createPortal } from 'react-dom';
import { api } from '@/lib/api';
import type { Score } from '@/lib/api';

interface LeaderboardContentProps {
  titleId?: string;
}

interface LeaderboardModalProps {
  isOpen: boolean;
  onClose: () => void;
}

function subscribeToDocumentBody() {
  return () => {};
}

function getDocumentBodySnapshot() {
  if (typeof document === 'undefined') return null;
  return document.body;
}

export function LeaderboardContent({ titleId }: LeaderboardContentProps) {
  const [scores, setScores] = useState<Score[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchScores = useCallback(async () => {
    try {
      const data = await api.getScores();
      setScores(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scores');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const timeout = setTimeout(fetchScores, 0);
    const interval = setInterval(fetchScores, 60000);
    return () => {
      clearTimeout(timeout);
      clearInterval(interval);
    };
  }, [fetchScores]);

  return (
    <>
      <div className="mb-6 flex items-center justify-between gap-4">
        <div>
          <h1 id={titleId} className="text-2xl font-bold">
            Leaderboard
          </h1>
          <p className="mt-1 text-sm text-gray-600">Top Aviator runs by money and awareness.</p>
        </div>
        <button
          type="button"
          onClick={fetchScores}
          className="rounded-md bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {loading && <p className="text-gray-600">Loading...</p>}
      {error && (
        <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </p>
      )}

      {!loading && !error && (
        <div className="overflow-x-auto">
          <table className="w-full min-w-[34rem] border-collapse text-sm">
            <thead>
              <tr className="border-b text-gray-500">
                <th className="py-2 pr-4 text-left font-medium">Rank</th>
                <th className="py-2 pr-4 text-left font-medium">Player</th>
                <th className="py-2 pr-4 text-left font-medium">Money</th>
                <th className="py-2 pr-4 text-left font-medium">Awareness</th>
                <th className="py-2 text-left font-medium">Last Active</th>
              </tr>
            </thead>
            <tbody>
              {scores.map((score, i) => (
                <tr key={`${score.name}-${score.created_at}`} className="border-b last:border-b-0">
                  <td className="py-2 pr-4">{i + 1}</td>
                  <td className="py-2 pr-4 font-medium">{score.name}</td>
                  <td className="py-2 pr-4">${score.money.toLocaleString()}</td>
                  <td className="py-2 pr-4">{score.global_awareness}</td>
                  <td className="py-2">{new Date(score.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}

export default function LeaderboardModal({ isOpen, onClose }: LeaderboardModalProps) {
  const portalRoot = useSyncExternalStore(
    subscribeToDocumentBody,
    getDocumentBodySnapshot,
    () => null,
  );

  if (!isOpen || !portalRoot) {
    return null;
  }

  const modal = (
    <div
      className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/55 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="leaderboard-modal-title"
      onClick={onClose}
    >
      <div
        className="max-h-[82vh] w-full max-w-3xl overflow-y-auto rounded-lg bg-white p-6 text-gray-950 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="mb-2 flex justify-end">
          <button
            type="button"
            onClick={onClose}
            className="text-2xl leading-none text-gray-400 hover:text-gray-700"
            aria-label="Close leaderboard"
          >
            ×
          </button>
        </div>
        <LeaderboardContent titleId="leaderboard-modal-title" />
      </div>
    </div>
  );

  return createPortal(modal, portalRoot);
}
