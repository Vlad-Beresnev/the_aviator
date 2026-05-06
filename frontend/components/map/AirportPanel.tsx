'use client';

import Link from 'next/link';
import { Airport } from '@/lib/api';

interface AirportPanelProps {
  airport: Airport;
  onClose: () => void;
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

export default function AirportPanel({ airport, onClose }: AirportPanelProps) {
  return (
    <div className="fixed right-0 top-0 h-full w-80 bg-white shadow-xl z-[1000] flex flex-col translate-x-0 transition-transform">
      <div className="flex items-start justify-between p-4 border-b">
        <div>
          <h2 className="font-bold text-lg leading-tight">{airport.name}</h2>
          <p className="text-sm text-gray-500">{airport.city} · {airport.continent}</p>
        </div>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 text-2xl leading-none ml-2 mt-0.5"
          aria-label="Close panel"
        >
          ×
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500 w-20">Level</span>
          <span className="font-medium">{airport.level}</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500 w-20">Difficulty</span>
          <Stars count={airport.difficulty} />
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500 w-20">Reward</span>
          <span className="font-medium">${airport.speaker_fee.toLocaleString()}</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-500 w-20">Status</span>
          <StatusBadge airport={airport} />
        </div>
      </div>

      <div className="p-4 border-t">
        {airport.locked ? (
          <button
            disabled
            className="w-full py-2 rounded bg-gray-200 text-gray-400 cursor-not-allowed font-medium"
          >
            Play Level
          </button>
        ) : (
          <Link
            href={`/game/${airport.ident}`}
            className="block w-full py-2 rounded bg-blue-600 text-white text-center font-medium hover:bg-blue-700 transition-colors"
          >
            Play Level
          </Link>
        )}
      </div>
    </div>
  );
}
