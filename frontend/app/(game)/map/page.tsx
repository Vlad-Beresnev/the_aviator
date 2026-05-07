'use client';

import dynamic from 'next/dynamic';
import { Suspense, useEffect, useRef, useState, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { api, Airport, AirportBounds } from '@/lib/api';
import AuthModal from '@/components/auth/AuthModal';
import AirportPanel from '@/components/map/AirportPanel';
import { useAuth } from '@/lib/auth';

const WorldMap = dynamic(() => import('@/components/map/WorldMap'), { ssr: false });

function MapContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { token, isLoading: isAuthLoading, logout } = useAuth();
  const [airports, setAirports] = useState<Airport[]>([]);
  const [selectedAirport, setSelectedAirport] = useState<Airport | null>(null);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(true);
  const [pendingLevelIdent, setPendingLevelIdent] = useState<string | null>(null);
  const airportFetchTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const airportFetchRequestRef = useRef(0);

  const initialLat = searchParams.get('lat') ? parseFloat(searchParams.get('lat')!) : 20;
  const initialLng = searchParams.get('lng') ? parseFloat(searchParams.get('lng')!) : 0;
  const initialZoom = searchParams.get('zoom') ? parseInt(searchParams.get('zoom')!, 10) : 3;

  useEffect(() => {
    return () => {
      if (airportFetchTimeoutRef.current) {
        clearTimeout(airportFetchTimeoutRef.current);
      }
    };
  }, []);

  const handleMapMove = useCallback(
    (lat: number, lng: number, zoom: number) => {
      router.replace(`/map?lat=${lat.toFixed(4)}&lng=${lng.toFixed(4)}&zoom=${zoom}`);
    },
    [router],
  );

  const handleMapBoundsChange = useCallback((bounds: AirportBounds) => {
    if (airportFetchTimeoutRef.current) {
      clearTimeout(airportFetchTimeoutRef.current);
    }

    airportFetchTimeoutRef.current = setTimeout(() => {
      const requestId = airportFetchRequestRef.current + 1;
      airportFetchRequestRef.current = requestId;

      api
        .getAirports(bounds)
        .then((nextAirports) => {
          if (airportFetchRequestRef.current === requestId) {
            setAirports(nextAirports);
          }
        })
        .catch(console.error);
    }, 150);
  }, []);

  const handleLogout = useCallback(() => {
    logout();
    setPendingLevelIdent(null);
    setIsAuthModalOpen(true);
  }, [logout]);

  const handleAuthButtonClick = useCallback(() => {
    if (token) {
      handleLogout();
      return;
    }

    setPendingLevelIdent(null);
    setIsAuthModalOpen(true);
  }, [handleLogout, token]);

  const handleRequireAuthForSelectedLevel = useCallback(() => {
    if (!selectedAirport) return;

    setPendingLevelIdent(selectedAirport.ident);
    setIsAuthModalOpen(true);
  }, [selectedAirport]);

  const handleAuthenticated = useCallback(() => {
    if (!pendingLevelIdent) return;

    router.push(`/game/${pendingLevelIdent}`);
    setPendingLevelIdent(null);
  }, [pendingLevelIdent, router]);

  const handleAuthModalClose = useCallback(() => {
    setPendingLevelIdent(null);
    setIsAuthModalOpen(false);
  }, []);

  return (
    <div className="relative h-screen w-screen overflow-hidden">
      <div className="absolute inset-0 z-0">
        <WorldMap
          airports={airports}
          onSelect={setSelectedAirport}
          onMapMove={handleMapMove}
          onBoundsChange={handleMapBoundsChange}
          initialCenter={[initialLat, initialLng]}
          initialZoom={initialZoom}
        />
      </div>

      <div
        className="absolute right-4 top-4 z-[900] flex items-end gap-2 rounded border border-white/15 bg-black/80 px-3 py-2 text-white shadow-lg backdrop-blur"
      >
        <button
          type="button"
          onClick={handleAuthButtonClick}
          className="rounded border border-white/15 bg-zinc-950 px-3 py-1 text-sm text-white outline-none hover:bg-zinc-800 focus:border-blue-400"
        >
          {token ? 'Logout' : 'Login'}
        </button>
      </div>

      {selectedAirport && (
        <AirportPanel
          airport={selectedAirport}
          onClose={() => setSelectedAirport(null)}
          isAuthenticated={Boolean(token)}
          onRequireAuth={handleRequireAuthForSelectedLevel}
        />
      )}
      <AuthModal
        isOpen={!isAuthLoading && !token && isAuthModalOpen}
        onClose={handleAuthModalClose}
        onAuthenticated={handleAuthenticated}
      />
    </div>
  );
}

export default function MapPage() {
  return (
    <Suspense fallback={<div className="h-screen w-screen bg-gray-100" />}>
      <MapContent />
    </Suspense>
  );
}
