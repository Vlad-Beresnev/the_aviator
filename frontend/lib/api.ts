export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface Airport {
  ident: string;
  name: string;
  city: string;
  latitude_deg: number;
  longitude_deg: number;
  continent: string;
  beaten: boolean;
  locked: boolean;
  level: number;
  difficulty: number;
  speaker_fee: number;
}

export interface GameState {
  id: number;
  name: string;
  money: number;
  battery_used: number;
  global_awareness: number;
  current_airport: string;
  won?: boolean;
  win_type?: string;
}

export interface Score {
  name: string;
  money: number;
  global_awareness: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token =
    typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers as Record<string, string> ?? {}),
  };

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `HTTP ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  register: (username: string, password: string) =>
    apiFetch<TokenResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  login: (username: string, password: string) =>
    apiFetch<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    }),

  getAirports: () => apiFetch<Airport[]>('/airports'),

  getAirport: (ident: string) => apiFetch<Airport>(`/airports/${ident}`),

  startGame: () => apiFetch<GameState>('/game/start', { method: 'POST' }),

  getGameState: () => apiFetch<GameState>('/game/state'),

  completeLevel: (airportIdent: string) =>
    apiFetch<GameState>('/game/complete-level', {
      method: 'POST',
      body: JSON.stringify({ airport_ident: airportIdent }),
    }),

  getScores: () => apiFetch<Score[]>('/scores'),
};
