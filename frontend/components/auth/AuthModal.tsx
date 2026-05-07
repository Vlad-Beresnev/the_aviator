'use client';

import { useState, useSyncExternalStore } from 'react';
import { createPortal } from 'react-dom';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';

type AuthMode = 'login' | 'register';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthenticated?: () => void;
}

function subscribeToDocumentBody() {
  return () => {};
}

function getDocumentBodySnapshot() {
  if (typeof document === 'undefined') return null;
  return document.body;
}

export default function AuthModal({ isOpen, onClose, onAuthenticated }: AuthModalProps) {
  const [mode, setMode] = useState<AuthMode>('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const portalRoot = useSyncExternalStore(
    subscribeToDocumentBody,
    getDocumentBodySnapshot,
    () => null,
  );
  const { login } = useAuth();

  if (!isOpen) return null;

  const isLogin = mode === 'login';

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const { access_token } = isLogin
        ? await api.login(username, password)
        : await api.register(username, password);
      login(access_token);
      onAuthenticated?.();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
    } finally {
      setIsSubmitting(false);
    }
  }

  function switchMode(nextMode: AuthMode) {
    setMode(nextMode);
    setError('');
  }

  const modal = (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 px-4">
      <div className="w-full max-w-sm rounded-lg bg-white p-6 text-gray-950 shadow-2xl">
        <div className="mb-5 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">{isLogin ? 'Log in' : 'Create account'}</h2>
            <p className="mt-1 text-sm text-gray-600">
              {isLogin ? 'Continue your Aviator run.' : 'Start saving your Aviator progress.'}
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-2xl leading-none text-gray-400 hover:text-gray-700"
            aria-label="Close authentication modal"
          >
            ×
          </button>
        </div>

        <div className="mb-4 grid grid-cols-2 rounded-md bg-gray-100 p-1">
          <button
            type="button"
            onClick={() => switchMode('login')}
            className={`rounded px-3 py-2 text-sm font-medium ${
              isLogin ? 'bg-white text-gray-950 shadow-sm' : 'text-gray-600 hover:text-gray-950'
            }`}
          >
            Log in
          </button>
          <button
            type="button"
            onClick={() => switchMode('register')}
            className={`rounded px-3 py-2 text-sm font-medium ${
              !isLogin ? 'bg-white text-gray-950 shadow-sm' : 'text-gray-600 hover:text-gray-950'
            }`}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <label className="block">
            <span className="mb-1 block text-sm font-medium text-gray-700">Username</span>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              autoComplete="username"
              required
            />
          </label>

          <label className="block">
            <span className="mb-1 block text-sm font-medium text-gray-700">Password</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 text-gray-950 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              autoComplete={isLogin ? 'current-password' : 'new-password'}
              required
            />
          </label>

          {error && (
            <p role="alert" className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full rounded-md bg-blue-600 px-4 py-2.5 font-medium text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-300"
          >
            {isSubmitting ? 'Please wait...' : isLogin ? 'Log in' : 'Register'}
          </button>
        </form>
      </div>
    </div>
  );

  if (!portalRoot) {
    return null;
  }

  return createPortal(modal, portalRoot);
}
