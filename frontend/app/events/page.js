import Link from 'next/link';

export default function EventsPage() {
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

      {/* Events Grid Scaffold */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
        gap: '1.5rem',
      }}>
        <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
          <div>
            <span className="badge badge-available" style={{ marginBottom: '1rem' }}>
              Live Seats Available
            </span>
            <h3 style={{ fontSize: '1.4rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
              FrontRow World Championship 2026
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem', lineHeight: 1.5 }}>
              Grand Arena • 100 Physical Seats • Multi-Tier Layout
            </p>
          </div>

          <Link href="/events/1" className="btn btn-primary" style={{ width: '100%' }}>
            View Seat Map & Reserve
          </Link>
        </div>
      </div>
    </div>
  );
}
