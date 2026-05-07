'use client';

import Link from 'next/link';
import { Airport } from '@/lib/api';

interface AirportPanelProps {
  airport: Airport;
  onClose: () => void;
  isAuthenticated: boolean;
  onRequireAuth: () => void;
}

function Stars({ count }: { count: number }) {
  return (
    <span>
      {Array.from({ length: 5 }, (_, i) => (
        <span key={i} className={i < count ? 'text-yellow-400' : 'text-gray-300'}>
          ★
        </span>
      ))}
    </span>
  );
}

function StatusBadge({ airport }: { airport: Airport }) {
  if (airport.beaten) {
    return <span className="inline-block px-2 py-0.5 rounded text-xs bg-green-100 text-green-700 font-medium">Beaten ✓</span>;
  }
  if (airport.locked) {
    return <span className="inline-block px-2 py-0.5 rounded text-xs bg-red-100 text-red-700 font-medium">Locked 🔒</span>;
  }
  return <span className="inline-block px-2 py-0.5 rounded text-xs bg-yellow-100 text-yellow-700 font-medium">Open</span>;
}

export default function AirportPanel({
  airport,
  onClose,
  isAuthenticated,
  onRequireAuth,
}: AirportPanelProps) {
  return (
    <div
      className="fixed inset-0 z-[1000] flex items-center justify-center bg-black/55 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="airport-modal-title"
      onClick={onClose}
    >
      <div
        className="w-full max-w-md rounded-lg bg-white text-gray-950 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="flex items-start justify-between gap-4 border-b p-5">
          <div>
            <h2 id="airport-modal-title" className="text-xl font-semibold leading-tight">
              {airport.name}
            </h2>
            <p className="mt-1 text-sm text-gray-600">
              {airport.city} · {airport.continent}
            </p>
          </div>
          <button
            onClick={onClose}
            className="text-2xl leading-none text-gray-400 hover:text-gray-700"
            aria-label="Close level details"
          >
            ×
          </button>
        </div>

        <div className="space-y-4 p-5">
          <p className="text-sm leading-6 text-gray-600">
            Plan this airport level before takeoff. Review the reward, difficulty, and current
            status, then start the flight challenge when you are ready.
          </p>

          <dl className="grid grid-cols-[7rem_1fr] gap-x-3 gap-y-3 text-sm">
            <dt className="text-gray-500">Level</dt>
            <dd className="font-medium">{airport.level}</dd>

            <dt className="text-gray-500">Difficulty</dt>
            <dd>
              <Stars count={airport.difficulty} />
            </dd>

            <dt className="text-gray-500">Reward</dt>
            <dd className="font-medium">${airport.speaker_fee.toLocaleString()}</dd>

            <dt className="text-gray-500">Status</dt>
            <dd>
              <StatusBadge airport={airport} />
            </dd>
          </dl>
        </div>

        <div className="border-t p-5">
          {airport.locked ? (
            <button
              disabled
              className="w-full rounded-md bg-gray-200 px-4 py-2.5 font-medium text-gray-400 cursor-not-allowed"
            >
              Play Level
            </button>
          ) : isAuthenticated ? (
            <Link
              href={`/game/${airport.ident}`}
              className="block w-full rounded-md bg-blue-600 px-4 py-2.5 text-center font-medium text-white transition-colors hover:bg-blue-700"
            >
              Play Level
            </Link>
          ) : (
            <button
              type="button"
              onClick={onRequireAuth}
              className="w-full rounded-md bg-blue-600 px-4 py-2.5 text-center font-medium text-white transition-colors hover:bg-blue-700"
            >
              Play Level
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
