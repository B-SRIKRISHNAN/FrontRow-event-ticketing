'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { getUser, removeToken, isAuthenticated } from '@/lib/auth';

export default function Navbar() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [user, setUserState] = useState(null);

  const syncAuth = () => {
    setLoggedIn(isAuthenticated());
    setUserState(getUser());
  };

  useEffect(() => {
    syncAuth();
    if (typeof window !== 'undefined') {
      window.addEventListener('auth-change', syncAuth);
      return () => window.removeEventListener('auth-change', syncAuth);
    }
  }, []);

  const handleLogout = () => {
    removeToken();
    setLoggedIn(false);
    setUserState(null);
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('auth-change'));
      window.location.href = '/login';
    }
  };

  return (
    <header style={{
      background: 'rgba(11, 15, 25, 0.85)',
      backdropFilter: 'blur(16px)',
      WebkitBackdropFilter: 'blur(16px)',
      borderBottom: '1px solid var(--border-glass)',
      position: 'sticky',
      top: 0,
      zIndex: 100,
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        paddingTop: '1rem',
        paddingBottom: '1rem',
      }}>
        {/* Brand Logo */}
        <Link href="/" style={{
          fontSize: '1.4rem',
          fontWeight: 800,
          background: 'var(--accent-gradient)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          letterSpacing: '-0.02em',
        }}>
          FrontRow
        </Link>

        {/* Nav Links */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <Link href="/events" style={{
            color: 'var(--text-secondary)',
            fontWeight: 500,
            fontSize: '0.95rem',
            transition: 'var(--transition-fast)',
          }}>
            Events
          </Link>
          <Link href="/orders" style={{
            color: 'var(--text-secondary)',
            fontWeight: 500,
            fontSize: '0.95rem',
            transition: 'var(--transition-fast)',
          }}>
            My Orders
          </Link>

          {/* User Auth Status & Buttons */}
          {loggedIn ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span style={{
                fontSize: '0.85rem',
                color: 'var(--text-muted)',
                background: 'rgba(255, 255, 255, 0.05)',
                padding: '0.35rem 0.75rem',
                borderRadius: 'var(--radius-full)',
                border: '1px solid var(--border-glass)',
              }}>
                {user?.email || 'Authenticated'}
              </span>
              <button onClick={handleLogout} className="btn btn-secondary" style={{ padding: '0.4rem 0.9rem', fontSize: '0.85rem' }}>
                Logout
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Link href="/login" className="btn btn-secondary" style={{ padding: '0.48rem 1rem', fontSize: '0.88rem' }}>
                Login
              </Link>
              <Link href="/register" className="btn btn-primary" style={{ padding: '0.48rem 1rem', fontSize: '0.88rem' }}>
                Register
              </Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
}
