'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, ApiError } from '@/lib/api';
import Toast from '@/components/Toast';

export default function EventsPage() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    async function fetchEvents() {
      try {
        setLoading(true);
        const data = await api.get('/api/v1/events');
        if (Array.isArray(data)) {
          setEvents(data);
        } else if (data && data.events) {
          setEvents(data.events);
        } else {
          setEvents([]);
        }
      } catch (err) {
        // Fallback demo event if backend not seeded or error
        setEvents([
          {
            id: 1,
            title: 'FrontRow World Championship 2026',
            venue: 'Grand Arena',
            capacity: 100,
            show_time: '2026-10-15 19:30',
          }
        ]);
        if (err instanceof ApiError && err.status !== 0) {
          setToast({ message: `Failed to load events: ${err.message}`, type: 'error' });
        }
      } finally {
        setLoading(false);
      }
    }

    fetchEvents();
  }, []);

  return (
    <div className="container">
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 900, marginBottom: '0.5rem' }}>
          Upcoming Events
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
          Browse available concerts, games, and shows to reserve seats in real time.
        </p>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-secondary)' }}>
          <p style={{ fontSize: '1.1rem', fontWeight: 500 }}>Loading events catalog...</p>
        </div>
      ) : events.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>No Events Scheduled</h3>
          <p style={{ color: 'var(--text-secondary)' }}>Check back soon for new event listings.</p>
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '1.5rem',
        }}>
          {events.map((evt) => (
            <div key={evt.id} className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
              <div>
                <span className="badge badge-available" style={{ marginBottom: '1rem' }}>
                  Live Seats Available
                </span>
                <h3 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                  {evt.title || evt.name || `Event #${evt.id}`}
                </h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem', lineHeight: 1.5 }}>
                  {evt.venue || 'Grand Arena'} • {evt.show_time || 'October 15, 2026'}
                </p>
              </div>

              <Link href={`/events/${evt.id}`} className="btn btn-primary" style={{ width: '100%' }}>
                View Seat Map & Reserve
              </Link>
            </div>
          ))}
        </div>
      )}

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
