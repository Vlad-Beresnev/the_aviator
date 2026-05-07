'use client';

import 'leaflet/dist/leaflet.css';
import 'react-leaflet-cluster/dist/assets/MarkerCluster.css';
import 'react-leaflet-cluster/dist/assets/MarkerCluster.Default.css';

import { useEffect, useMemo, useRef } from 'react';
import L from 'leaflet';
import { MapContainer, Marker, useMap, useMapEvents } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import { Airport, AirportBounds } from '@/lib/api';
import { MAP_THEMES } from './mapThemes';

const WORLD_SOUTH = -85.05112878;
const WORLD_NORTH = 85.05112878;
const MIN_ZOOM = 3;
const MAX_NATIVE_ZOOM = 17;
const DISABLE_CLUSTERING_AT_ZOOM = 10;

function wrapNumber(value: number, min: number, max: number): number {
  const range = max - min;
  return ((((value - min) % range) + range) % range) + min;
}

function wrapTileCoordinate(value: number, tileCount: number): number {
  return ((value % tileCount) + tileCount) % tileCount;
}

function normalizeWorldPosition(lat: number, lng: number): L.LatLngExpression {
  return [
    wrapNumber(lat, WORLD_SOUTH, WORLD_NORTH),
    wrapNumber(lng, -180, 180),
  ];
}

function hasMovedAcrossWorldEdge(current: L.LatLng, normalized: L.LatLngExpression): boolean {
  const [lat, lng] = normalized as [number, number];
  return Math.abs(current.lat - lat) > 0.000001 || Math.abs(current.lng - lng) > 0.000001;
}

function clampZoom(zoom: number): number {
  return Math.max(zoom, MIN_ZOOM);
}

function normalizeMapBounds(bounds: L.LatLngBounds): AirportBounds {
  const south = Math.max(bounds.getSouth(), WORLD_SOUTH);
  const north = Math.min(bounds.getNorth(), WORLD_NORTH);
  const west = bounds.getWest();
  const east = bounds.getEast();

  if (east - west >= 360) {
    return { south, north, west: -180, east: 180 };
  }

  return {
    south,
    north,
    west: wrapNumber(west, -180, 180),
    east: wrapNumber(east, -180, 180),
  };
}

function makeIcon(color: string) {
  return L.divIcon({
    className: '',
    html: `<div style="width:12px;height:12px;border-radius:50%;background:${color};border:2px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.4)"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  });
}

function difficultyBucket(difficulty: number): 'easy' | 'medium' | 'hard' {
  if (difficulty <= 2) return 'easy';
  if (difficulty >= 4) return 'hard';
  return 'medium';
}

class WrappedWorldTileLayer extends L.TileLayer {
  getTileUrl(coords: L.Coords): string {
    const tileCount = 2 ** coords.z;
    const wrappedCoords = L.point(
      wrapTileCoordinate(coords.x, tileCount),
      wrapTileCoordinate(coords.y, tileCount),
    ) as L.Coords;

    wrappedCoords.z = coords.z;
    return super.getTileUrl(wrappedCoords);
  }
}

interface WrappedTileLayerProps {
  url: string;
  attribution: string;
}

function WrappedTileLayer({ url, attribution }: WrappedTileLayerProps) {
  const map = useMap();

  useEffect(() => {
    const layer = new WrappedWorldTileLayer(url, {
      attribution,
      minZoom: MIN_ZOOM,
      maxNativeZoom: MAX_NATIVE_ZOOM,
      updateWhenIdle: true,
      updateWhenZooming: false,
      keepBuffer: 1,
      noWrap: false,
    });

    layer.addTo(map);
    return () => {
      layer.removeFrom(map);
    };
  }, [attribution, map, url]);

  return null;
}

interface MapEventsProps {
  onMapMove: (lat: number, lng: number, zoom: number) => void;
  onBoundsChange: (bounds: AirportBounds) => void;
  onMapClick: () => void;
  markerClickedRef: React.RefObject<boolean>;
}

function MapEvents({ onMapMove, onBoundsChange, onMapClick, markerClickedRef }: MapEventsProps) {
  const isWrappingRef = useRef(false);

  const map = useMapEvents({
    moveend(e) {
      const map = e.target;
      if (isWrappingRef.current) {
        isWrappingRef.current = false;
        onBoundsChange(normalizeMapBounds(map.getBounds()));
        return;
      }

      const center = map.getCenter();
      const zoom = map.getZoom();
      const normalizedCenter = normalizeWorldPosition(center.lat, center.lng);

      if (hasMovedAcrossWorldEdge(center, normalizedCenter)) {
        isWrappingRef.current = true;
        map.setView(normalizedCenter, zoom, { animate: false });
        const [lat, lng] = normalizedCenter as [number, number];
        onMapMove(lat, lng, zoom);
        onBoundsChange(normalizeMapBounds(map.getBounds()));
        return;
      }

      onMapMove(center.lat, center.lng, zoom);
      onBoundsChange(normalizeMapBounds(map.getBounds()));
    },
    click() {
      if (markerClickedRef.current) {
        markerClickedRef.current = false;
        return;
      }
      onMapClick();
    },
  });

  useEffect(() => {
    onBoundsChange(normalizeMapBounds(map.getBounds()));
  }, [map, onBoundsChange]);

  return null;
}

interface WorldMapProps {
  airports: Airport[];
  onSelect: (airport: Airport | null) => void;
  onMapMove: (lat: number, lng: number, zoom: number) => void;
  onBoundsChange: (bounds: AirportBounds) => void;
  initialCenter?: [number, number];
  initialZoom?: number;
}

export default function WorldMap({
  airports,
  onSelect,
  onMapMove,
  onBoundsChange,
  initialCenter = [20, 0],
  initialZoom = 3,
}: WorldMapProps) {
  const markerClickedRef = useRef(false);
  const activeTheme = MAP_THEMES.openTopo;
  const normalizedInitialCenter = normalizeWorldPosition(initialCenter[0], initialCenter[1]);
  const markerIcons = useMemo(
    () => ({
      easy: makeIcon('#22c55e'),
      medium: makeIcon('#eab308'),
      hard: makeIcon('#ef4444'),
    }),
    [],
  );

  return (
    <MapContainer
      center={normalizedInitialCenter}
      zoom={clampZoom(initialZoom)}
      minZoom={MIN_ZOOM}
      worldCopyJump
      style={{ height: '100%', width: '100%' }}
    >
      <WrappedTileLayer
        url={activeTheme.url}
        attribution={activeTheme.attribution}
      />
      <MapEvents
        onMapMove={onMapMove}
        onBoundsChange={onBoundsChange}
        onMapClick={() => onSelect(null)}
        markerClickedRef={markerClickedRef}
      />
      <MarkerClusterGroup
        chunkedLoading
        removeOutsideVisibleBounds
        disableClusteringAtZoom={DISABLE_CLUSTERING_AT_ZOOM}
      >
        {airports.map((airport) => (
          <Marker
            key={airport.ident}
            position={[airport.latitude_deg, airport.longitude_deg]}
            icon={markerIcons[difficultyBucket(airport.difficulty)]}
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
