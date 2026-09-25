'use client';

import { useState, useEffect } from 'react';

export default function CountdownTimer({ expiresAt, initialSeconds = 300, onExpire }) {
  const [secondsLeft, setSecondsLeft] = useState(() => {
    if (expiresAt) {
      const expTime = new Date(expiresAt).getTime();
      const nowTime = new Date().getTime();
      const diff = Math.floor((expTime - nowTime) / 1000);
      return diff > 0 ? diff : 0;
    }
    return initialSeconds;
  });

  useEffect(() => {
    if (secondsLeft <= 0) {
      if (onExpire) onExpire();
      return;
    }

    const interval = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          if (onExpire) onExpire();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [expiresAt, secondsLeft, onExpire]);

  const minutes = Math.floor(secondsLeft / 60);
  const seconds = secondsLeft % 60;
  const formatted = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  const isWarning = secondsLeft > 0 && secondsLeft < 60;

  return (
    <div
      className={isWarning ? 'pulse-warning' : ''}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '0.5rem',
        padding: '0.4rem 0.85rem',
        borderRadius: 'var(--radius-full)',
        background: isWarning ? 'var(--error-bg)' : 'rgba(99, 102, 241, 0.15)',
        border: `1px solid ${isWarning ? 'var(--error-crimson)' : 'var(--accent-indigo)'}`,
        color: isWarning ? 'var(--error-crimson)' : 'var(--accent-indigo)',
        fontWeight: 800,
        fontFamily: 'monospace',
        fontSize: '1rem',
      }}
    >
      <span style={{ fontSize: '0.8rem' }}>⏱ Hold Lease:</span>
      <span>{formatted}</span>
    </div>
  );
}
