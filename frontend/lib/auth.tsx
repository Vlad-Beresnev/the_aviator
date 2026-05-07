'use client';

import { createContext, useContext, useSyncExternalStore } from 'react';
import type { ReactNode } from 'react';

interface AuthContextValue {
  token: string | null;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);
const TOKEN_CHANGED_EVENT = 'aviator-token-changed';

function getCookieValue(name: string) {
  if (typeof document === 'undefined') return null;
  const cookie = document.cookie
    .split('; ')
    .find((item) => item.startsWith(`${name}=`));
  return cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : null;
}

function getTokenSnapshot() {
  if (typeof window === 'undefined') return null;
  const token = localStorage.getItem('token');
  const cookieToken = getCookieValue('auth_token');

  return token && cookieToken ? token : null;
}

function subscribeToTokenChanges(onChange: () => void) {
  window.addEventListener('storage', onChange);
  window.addEventListener(TOKEN_CHANGED_EVENT, onChange);

  return () => {
    window.removeEventListener('storage', onChange);
    window.removeEventListener(TOKEN_CHANGED_EVENT, onChange);
  };
}

function emitTokenChanged() {
  window.dispatchEvent(new Event(TOKEN_CHANGED_EVENT));
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const token = useSyncExternalStore(subscribeToTokenChanges, getTokenSnapshot, () => null);

  function login(t: string) {
    localStorage.setItem('token', t);
    document.cookie = `auth_token=${t}; path=/; SameSite=Lax`;
    emitTokenChanged();
  }

  function logout() {
    localStorage.removeItem('token');
    document.cookie = 'auth_token=; path=/; max-age=0';
    emitTokenChanged();
  }

  return (
    <AuthContext.Provider value={{ token, isLoading: false, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
