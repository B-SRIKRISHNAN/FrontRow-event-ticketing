export default function OrdersPage() {
  return (
    <div className="container">
      <div style={{ marginBottom: '2.5rem' }}>
        <h1 style={{ fontSize: '2.2rem', fontWeight: 900, marginBottom: '0.5rem' }}>
          My Order History
        </h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1rem' }}>
          View confirmed ticket purchases and order references.
        </p>
      </div>

      <div className="glass-card" style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
        <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>🎟️</div>
        <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
          No Orders Purchased Yet
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', maxWidth: '400px', margin: '0 auto 1.5rem' }}>
          When you complete checkout for seat reservations, your confirmed tickets will appear here.
        </p>
      </div>
    </div>
  );
}
