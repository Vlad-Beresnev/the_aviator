'use client';

import dynamic from 'next/dynamic';
import { useEffect, useState, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { api, Airport } from '@/lib/api';
import AirportPanel from '@/components/map/AirportPanel';

const WorldMap = dynamic(() => import('@/components/map/WorldMap'), { ssr: false });

export default function MapPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [airports, setAirports] = useState<Airport[]>([]);
  const [selectedAirport, setSelectedAirport] = useState<Airport | null>(null);

  const initialLat = searchParams.get('lat') ? parseFloat(searchParams.get('lat')!) : 20;
  const initialLng = searchParams.get('lng') ? parseFloat(searchParams.get('lng')!) : 0;
  const initialZoom = searchParams.get('zoom') ? parseInt(searchParams.get('zoom')!, 10) : 3;

  useEffect(() => {
    api.getAirports().then(setAirports).catch(console.error);
  }, []);

  const handleMapMove = useCallback(
    (lat: number, lng: number, zoom: number) => {
      router.replace(`/map?lat=${lat.toFixed(4)}&lng=${lng.toFixed(4)}&zoom=${zoom}`);
    },
    [router],
  );

  return (
    <div className="relative h-screen w-screen">
      <WorldMap
        airports={airports}
        onSelect={setSelectedAirport}
        onMapMove={handleMapMove}
        initialCenter={[initialLat, initialLng]}
        initialZoom={initialZoom}
      />
      {selectedAirport && (
        <AirportPanel airport={selectedAirport} onClose={() => setSelectedAirport(null)} />
      )}
    </div>
  );
}
