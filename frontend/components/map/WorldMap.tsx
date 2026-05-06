'use client';

import 'leaflet/dist/leaflet.css';
import 'react-leaflet-cluster/dist/assets/MarkerCluster.css';
import 'react-leaflet-cluster/dist/assets/MarkerCluster.Default.css';

import { useRef } from 'react';
import L from 'leaflet';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import { Airport } from '@/lib/api';

function markerColor(airport: Airport): string {
  if (airport.beaten) return '#22c55e';
  if (airport.locked) return '#ef4444';
  return '#eab308';
}

function makeIcon(color: string) {
  return L.divIcon({
    className: '',
    html: `<div style="width:12px;height:12px;border-radius:50%;background:${color};border:2px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.4)"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  });
}

interface MapEventsProps {
  onMapMove: (lat: number, lng: number, zoom: number) => void;
  onMapClick: () => void;
  markerClickedRef: React.RefObject<boolean>;
}

function MapEvents({ onMapMove, onMapClick, markerClickedRef }: MapEventsProps) {
  useMapEvents({
    moveend(e) {
      const map = e.target;
      const center = map.getCenter();
      onMapMove(center.lat, center.lng, map.getZoom());
    },
    click() {
      if (markerClickedRef.current) {
        markerClickedRef.current = false;
        return;
      }
      onMapClick();
    },
  });
  return null;
}

interface WorldMapProps {
  airports: Airport[];
  onSelect: (airport: Airport | null) => void;
  onMapMove: (lat: number, lng: number, zoom: number) => void;
  initialCenter?: [number, number];
  initialZoom?: number;
}

export default function WorldMap({
  airports,
  onSelect,
  onMapMove,
  initialCenter = [20, 0],
  initialZoom = 3,
}: WorldMapProps) {
  const markerClickedRef = useRef(false);

  return (
    <MapContainer
      center={initialCenter}
      zoom={initialZoom}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />
      <MapEvents
        onMapMove={onMapMove}
        onMapClick={() => onSelect(null)}
        markerClickedRef={markerClickedRef}
      />
      <MarkerClusterGroup>
        {airports.map((airport) => (
          <Marker
            key={airport.ident}
            position={[airport.latitude_deg, airport.longitude_deg]}
            icon={makeIcon(markerColor(airport))}
            eventHandlers={{
              click() {
                markerClickedRef.current = true;
                onSelect(airport);
              },
            }}
          />
        ))}
      </MarkerClusterGroup>
    </MapContainer>
  );
}
