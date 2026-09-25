'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, ApiError } from '@/lib/api';
import { isAuthenticated } from '@/lib/auth';
import Toast from '@/components/Toast';

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState(null);

  useEffect(() => {
    async function fetchOrders() {
      if (!isAuthenticated()) {
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const data = await api.get('/api/v1/orders');
        const orderList = Array.isArray(data) ? data : data?.orders || [];
        setOrders(orderList);
      } catch (err) {
        if (err instanceof ApiError && err.status !== 0) {
          setToast({ message: `Failed to load order history: ${err.message}`, type: 'error' });
        }
        setOrders([]);
      } finally {
        setLoading(false);
      }
    }

    fetchOrders();
  }, []);

  if (!isAuthenticated() && !loading) {
    return (
      <div className="container" style={{ maxWidth: '500px', paddingTop: '4rem' }}>
        <div className="glass-card" style={{ textAlign: 'center', padding: '3rem 2rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔒</div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '0.5rem' }}>
            Authentication Required
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', marginBottom: '1.5rem' }}>
            Please sign in to view your confirmed ticket purchases and order receipts.
          </p>
          <Link href="/login" className="btn btn-primary" style={{ display: 'inline-block', padding: '0.75rem 1.5rem' }}>
            Sign In to View Orders
          </Link>
        </div>
      </div>
    );
  }

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

      {loading ? (
        <div style={{ textAlign: 'center', padding: '4rem 0', color: 'var(--text-secondary)' }}>
          <p style={{ fontSize: '1.1rem', fontWeight: 500 }}>Loading order receipts...</p>
        </div>
      ) : orders.length === 0 ? (
        <div className="glass-card" style={{ textAlign: 'center', padding: '3.5rem 1.5rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎟️</div>
          <h3 style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
            No Orders Purchased Yet
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', maxWidth: '420px', margin: '0 auto 1.75rem', lineHeight: 1.5 }}>
            When you complete checkout for seat reservations, your confirmed tickets and receipt breakdown will appear here.
          </p>
          <Link href="/events" className="btn btn-primary" style={{ padding: '0.75rem 1.5rem' }}>
            Browse Events & Select Seats
          </Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {orders.map((order) => {
            const createdDate = order.created_at
              ? new Date(order.created_at).toLocaleString()
              : 'Recently Purchased';
            const total = Number(order.total_amount || 0).toFixed(2);
            const tickets = order.tickets || [];

            return (
              <div key={order.id} className="glass-card" style={{ borderLeft: '4px solid var(--status-available)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
                  <div>
                    <span className="badge badge-available" style={{ marginBottom: '0.5rem' }}>
                      Confirmed Purchase
                    </span>
                    <h3 style={{ fontSize: '1.3rem', fontWeight: 800 }}>
                      Order #{order.id}
                    </h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
                      Purchased: {createdDate}
                    </p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Total Amount
                    </span>
                    <div style={{ fontSize: '1.5rem', fontWeight: 900, color: 'var(--accent-indigo)' }}>
                      ${total}
                    </div>
                  </div>
                </div>

                {/* Tickets Breakdown */}
                <div style={{ borderTop: '1px solid var(--border-glass)', paddingTop: '1rem' }}>
                  <h4 style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
                    Issued Tickets ({tickets.length})
                  </h4>
                  <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
                    {tickets.map((ticket) => (
                      <div
                        key={ticket.id}
                        style={{
                          background: 'rgba(255, 255, 255, 0.04)',
                          border: '1px solid var(--border-glass-bright)',
                          borderRadius: 'var(--radius-sm)',
                          padding: '0.5rem 0.85rem',
                          fontSize: '0.88rem',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem',
                        }}
                      >
                        <span style={{ color: 'var(--accent-indigo)', fontWeight: 800 }}>🎫</span>
                        <span style={{ fontWeight: 600 }}>Seat #{ticket.seat_id}</span>
                        <span style={{ color: 'var(--text-muted)' }}>•</span>
                        <span style={{ color: 'var(--text-secondary)' }}>${Number(ticket.price_paid || 0).toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
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
