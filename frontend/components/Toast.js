'use client';

import { useEffect } from 'react';

export default function Toast({ message, type = 'error', onClose, autoDismissMs = 4000 }) {
  useEffect(() => {
    if (!autoDismissMs || !onClose) return;
    const timer = setTimeout(() => {
      onClose();
    }, autoDismissMs);
    return () => clearTimeout(timer);
  }, [message, type, onClose, autoDismissMs]);

  if (!message) return null;

  const isError = type === 'error';
  const isSuccess = type === 'success';

  let bg = 'rgba(15, 23, 42, 0.95)';
  let border = 'var(--border-glass-bright)';
  let text = 'var(--text-primary)';
  let icon = 'ℹ️';

  if (isError) {
    bg = 'rgba(239, 68, 68, 0.92)';
    border = '#dc2626';
    text = '#ffffff';
    icon = '⚠️';
  } else if (isSuccess) {
    bg = 'rgba(16, 185, 129, 0.92)';
    border = '#059669';
    text = '#ffffff';
    icon = '✅';
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '24px',
        right: '24px',
        zIndex: 9999,
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        padding: '0.9rem 1.25rem',
        borderRadius: 'var(--radius-md)',
        background: bg,
        border: `1px solid ${border}`,
        color: text,
        boxShadow: '0 10px 30px rgba(0, 0, 0, 0.5)',
        backdropFilter: 'blur(12px)',
        fontSize: '0.95rem',
        fontWeight: 600,
        maxWidth: '420px',
        animation: 'slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)',
      }}
    >
      <span style={{ fontSize: '1.2rem' }}>{icon}</span>
      <span style={{ flex: 1, lineHeight: 1.4 }}>{message}</span>
      {onClose && (
        <button
          onClick={onClose}
          style={{
            background: 'none',
            border: 'none',
            color: 'inherit',
            fontSize: '1.2rem',
            cursor: 'pointer',
            opacity: 0.8,
            padding: '0 4px',
          }}
        >
          ×
        </button>
      )}
    </div>
  );
}
