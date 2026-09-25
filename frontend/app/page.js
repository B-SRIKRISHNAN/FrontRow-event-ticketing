import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="container">
      {/* Hero Section */}
      <section style={{
        textAlign: 'center',
        padding: '4rem 1rem 3rem',
        maxWidth: '900px',
        margin: '0 auto',
      }}>
        <span className="badge badge-available" style={{ marginBottom: '1.25rem', fontSize: '0.85rem' }}>
          ⚡ Ultra-Low Latency Seat Reservations
        </span>
        <h1 style={{
          fontSize: '3.2rem',
          fontWeight: 900,
          lineHeight: 1.15,
          letterSpacing: '-0.03em',
          marginBottom: '1.5rem',
          background: 'var(--accent-gradient)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
        }}>
          FrontRow Event Ticketing
        </h1>
        <p style={{
          fontSize: '1.2rem',
          color: 'var(--text-secondary)',
          lineHeight: 1.6,
          marginBottom: '2.5rem',
        }}>
          Experience zero double-selling ticket booking powered by non-blocking row locking, 
          tri-layer hold leases, and AI-driven candidate seat recommendations.
        </p>

        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <Link href="/events" className="btn btn-primary" style={{ padding: '0.9rem 2rem', fontSize: '1.05rem' }}>
            Browse Upcoming Events
          </Link>
          <Link href="/login" className="btn btn-secondary" style={{ padding: '0.9rem 2rem', fontSize: '1.05rem' }}>
            Sign In to Account
          </Link>
        </div>
      </section>

      {/* Feature Highlights Grid */}
      <section style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '1.5rem',
        marginTop: '3rem',
      }}>
        <div className="glass-card">
          <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>🔒</div>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
            Zero Double-Selling
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.5 }}>
            PostgreSQL non-blocking row locks (<code style={{ color: 'var(--accent-indigo)' }}>NOWAIT</code>) guarantee instant 409 Conflict resolution without app-level bottlenecking.
          </p>
        </div>

        <div className="glass-card">
          <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>⏱️</div>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
            Tri-Layer Lease Lifecycle
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.5 }}>
            5-minute reservation lease window enforced across lazy read expiration, atomic lock overwrite, and asynchronous background worker cleanup.
          </p>
        </div>

        <div className="glass-card">
          <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>🤖</div>
          <h3 style={{ fontSize: '1.2rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
            AI Seat Search Engine
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.5 }}>
            Decoupled LLM microservice parses natural language queries into structured parameters with single-row contiguity seat matching.
          </p>
        </div>
      </section>
    </div>
  );
}
