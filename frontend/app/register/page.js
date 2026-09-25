'use client';

import { useState } from 'react';
import Link from 'next/link';
import { api, ApiError } from '@/lib/api';
import { setToken, setUser } from '@/lib/auth';
import Toast from '@/components/Toast';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) return;

    if (password.length < 8) {
      setToast({ message: 'Password must be at least 8 characters long.', type: 'error' });
      return;
    }

    setLoading(true);
    setToast(null);

    try {
      const res = await api.post('/api/v1/auth/register', { email, password });
      const token = res.access_token;
      if (token) {
        setToken(token);
        setUser({ email });
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('auth-change'));
          window.location.href = '/events';
        }
      } else {
        setToast({ message: 'Registration succeeded but no token received. Please log in.', type: 'error' });
      }
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Registration failed. Please try again.';
      setToast({ message: msg, type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ maxWidth: '440px', paddingTop: '4rem' }}>
      <div className="glass-card">
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.5rem', textAlign: 'center' }}>
          Create Account
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', textAlign: 'center', marginBottom: '2rem' }}>
          Register to unlock real-time seat holds and AI recommendations
        </p>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Email Address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="user@example.com"
              className="input-field"
              required
            />
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '0.4rem' }}>
              Password (min 8 characters)
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="input-field"
              minLength={8}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ marginTop: '0.5rem', padding: '0.85rem' }}
          >
            {loading ? 'Creating Account...' : 'Register Account'}
          </button>
        </form>

        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
          Already registered?{' '}
          <Link href="/login" style={{ color: 'var(--accent-indigo)', fontWeight: 600 }}>
            Sign in here
          </Link>
        </div>
      </div>

      {toast && (
        <Toast
          message={toast.message}
          type={toast.type}
          onClose={() => setToast(null)}
        />
      )}
    </div>
  );
}
