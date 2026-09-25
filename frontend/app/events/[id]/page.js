'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { api, ApiError } from '@/lib/api';
import { isAuthenticated } from '@/lib/auth';
import SeatGridCell from '@/components/SeatGridCell';
import CountdownTimer from '@/components/CountdownTimer';
import Toast from '@/components/Toast';

export default function EventDetailPage({ params }) {
  const eventId = params?.id || '1';
  const [seats, setSeats] = useState([]);
  const [eventDetails, setEventDetails] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedSeatIds, setSelectedSeatIds] = useState([]);
  const [activeHold, setActiveHold] = useState(null);

  // Loading & submission state
  const [holdLoading, setHoldLoading] = useState(false);
  const [checkoutLoading, setCheckoutLoading] = useState(false);
  const [aiQuery, setAiQuery] = useState('');
  const [aiLoading, setAiLoading] = useState(false);

  // Toast notifications
  const [toast, setToast] = useState(null);

  const showToast = (message, type = 'error') => {
    setToast({ message, type });
  };

  // Fetch seat map
  const fetchSeatMap = useCallback(async (isSilent = false) => {
    try {
      if (!isSilent) setLoading(true);
      const res = await api.get(`/api/v1/events/${eventId}/seats`);
      const seatList = res?.seats || (Array.isArray(res) ? res : []);
      setSeats(seatList);
      if (res?.event_title || res?.venue_name) {
        setEventDetails({
          title: res.event_title || `Event #${eventId}`,
          venue: res.venue_name || 'Grand Arena',
        });
      }
    } catch (err) {
      if (!isSilent) {
        // Fallback demo grid if backend endpoint is unavailable
        const demoSeats = Array.from({ length: 24 }, (_, i) => {
          const row = String.fromCharCode(65 + Math.floor(i / 6));
          const num = (i % 6) + 1;
          let status = 'AVAILABLE';
          if (i === 3 || i === 10) status = 'LOCKED';
          if (i === 5 || i === 12) status = 'SOLD';
          return {
            id: i + 1,
            event_id: Number(eventId),
            row,
            seat_number: num,
            section: row === 'A' ? 'VIP' : 'Standard',
            price: row === 'A' ? 150 : 85,
            status,
          };
        });
        setSeats(demoSeats);
        if (err instanceof ApiError && err.status !== 0) {
          showToast(`Failed to load live seat map: ${err.message}`, 'error');
        }
      }
    } finally {
      if (!isSilent) setLoading(false);
    }
  }, [eventId]);

  // Initial load & 4-second polling loop
  useEffect(() => {
    fetchSeatMap(false);

    const pollInterval = setInterval(() => {
      fetchSeatMap(true);
    }, 4000);

    return () => clearInterval(pollInterval);
  }, [fetchSeatMap]);

  // Clean up selected seats if they become locked or sold during polling
  useEffect(() => {
    if (selectedSeatIds.length > 0 && seats.length > 0) {
      const validSelected = selectedSeatIds.filter((id) => {
        const seat = seats.find((s) => s.id === id);
        return seat && seat.status === 'AVAILABLE';
      });
      if (validSelected.length !== selectedSeatIds.length && !activeHold) {
        setSelectedSeatIds(validSelected);
        showToast('One or more selected seats were reserved by another user.', 'error');
      }
    }
  }, [seats, activeHold, selectedSeatIds]);

  // Seat toggle handler
  const handleSeatClick = (seat) => {
    if (activeHold) {
      showToast('You currently have an active hold. Complete checkout or wait for expiry.', 'info');
      return;
    }
    if (seat.status !== 'AVAILABLE') return;

    setSelectedSeatIds((prev) =>
      prev.includes(seat.id) ? prev.filter((id) => id !== seat.id) : [...prev, seat.id]
    );
  };

  // Hold lease handler
  const handleHoldSeats = async () => {
    if (!isAuthenticated()) {
      showToast('Please log in to hold seats.', 'error');
      setTimeout(() => {
        if (typeof window !== 'undefined') window.location.href = '/login';
      }, 1500);
      return;
    }

    if (selectedSeatIds.length === 0) {
      showToast('Please select at least one available seat to hold.', 'error');
      return;
    }

    setHoldLoading(true);
    try {
      const res = await api.post(`/api/v1/events/${eventId}/holds`, {
        seat_ids: selectedSeatIds,
      });

      setActiveHold({
        hold_id: res.hold_id,
        expires_at: res.expires_at,
        seat_ids: res.seat_ids || selectedSeatIds,
      });

      showToast('Hold lease acquired! You have 5 minutes to complete checkout.', 'success');
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        showToast('Hold failed: Lock conflict or selected seats are no longer available.', 'error');
      } else {
        const msg = err instanceof ApiError ? err.message : 'Failed to acquire hold. Please try again.';
        showToast(msg, 'error');
      }
      setSelectedSeatIds([]);
      fetchSeatMap(true);
    } finally {
      setHoldLoading(false);
    }
  };

  // Checkout handler
  const handleCheckout = async () => {
    if (!activeHold) return;

    setCheckoutLoading(true);
    try {
      await api.post(`/api/v1/checkout/holds/${activeHold.hold_id}`, {
        payment_token: 'tok_mock_success_frontend',
      });

      showToast('Checkout successful! Confirmation order created.', 'success');
      setActiveHold(null);
      setSelectedSeatIds([]);

      setTimeout(() => {
        if (typeof window !== 'undefined') window.location.href = '/orders';
      }, 1200);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        showToast('Checkout failed: Hold lease expired or seats already purchased.', 'error');
      } else {
        const msg = err instanceof ApiError ? err.message : 'Checkout failed. Please try again.';
        showToast(msg, 'error');
      }
      setActiveHold(null);
      setSelectedSeatIds([]);
      fetchSeatMap(true);
    } finally {
      setCheckoutLoading(false);
    }
  };

  // Hold expiry callback from CountdownTimer
  const handleHoldExpired = () => {
    if (activeHold) {
      setActiveHold(null);
      setSelectedSeatIds([]);
      showToast('Hold lease expired! Seats released back to live availability.', 'error');
      fetchSeatMap(true);
    }
  };

  // AI Natural Language Search handler
  const handleAISearch = async (e) => {
    e.preventDefault();
    if (!aiQuery.trim()) return;

    setAiLoading(true);
    try {
      const res = await api.post(`/api/v1/events/${eventId}/ai-search`, {
        query: aiQuery.trim(),
      });

      const candidates = res.recommended_seat_ids || res.candidate_seats || [];
      const fallback = res.fallback_to_manual;

      if (candidates.length > 0) {
        setSelectedSeatIds(candidates);
        showToast(`AI matched ${candidates.length} seat(s) matching your prompt!`, 'success');
      } else if (fallback) {
        showToast('AI recommendation unavailable or no exact match found. Please select seats manually on the grid.', 'info');
      } else {
        showToast('No matching seats found for your search criteria.', 'info');
      }
    } catch (err) {
      showToast('AI recommendation engine unreachable. Please pick seats manually.', 'info');
    } finally {
      setAiLoading(false);
    }
  };

  // Group seats by row for structured map layout
  const rowsMap = seats.reduce((acc, seat) => {
    const r = seat.row || 'A';
    if (!acc[r]) acc[r] = [];
    acc[r].push(seat);
    return acc;
  }, {});

  const selectedTotal = selectedSeatIds.reduce((sum, id) => {
    const seat = seats.find((s) => s.id === id);
    return sum + (seat ? Number(seat.price) : 0);
  }, 0);

  return (
    <div className="container">
      {/* Event Header & Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1.5rem', marginBottom: '2rem' }}>
        <div>
          <span className="badge badge-available" style={{ marginBottom: '0.5rem' }}>
            Live Seat Map • 4s Polling
          </span>
          <h1 style={{ fontSize: '2.2rem', fontWeight: 900, marginBottom: '0.4rem' }}>
            {eventDetails?.title || `Event #${eventId}`}
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            {eventDetails?.venue || 'Grand Arena'} • Click available seats to select
          </p>
        </div>

        {activeHold && (
          <CountdownTimer
            expiresAt={activeHold.expires_at}
            onExpire={handleHoldExpired}
          />
        )}
      </div>

      {/* AI Seat Search Box (US5) */}
      <div className="glass-card" style={{ marginBottom: '2rem', padding: '1.25rem 1.5rem' }}>
        <form onSubmit={handleAISearch} style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: 1, minWidth: '260px' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-indigo)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.3rem' }}>
              ✨ AI Smart Seat Finder
            </label>
            <input
              type="text"
              value={aiQuery}
              onChange={(e) => setAiQuery(e.target.value)}
              placeholder="e.g. Find me 2 seats together under $100 in section A"
              className="input-field"
              style={{ fontSize: '0.92rem', padding: '0.6rem 1rem' }}
            />
          </div>
          <button
            type="submit"
            className="btn btn-secondary"
            disabled={aiLoading}
            style={{ marginTop: 'auto', padding: '0.65rem 1.25rem', fontSize: '0.9rem' }}
          >
            {aiLoading ? 'Searching...' : '✨ Find Seats'}
          </button>
        </form>
      </div>

      {/* Interactive Seat Map (US2 & US3) */}
      <div className="glass-card" style={{ marginBottom: '2rem', textAlign: 'center', minHeight: '320px' }}>
        <div style={{
          background: 'rgba(99, 102, 241, 0.1)',
          borderBottom: '1px solid var(--border-glass)',
          padding: '0.6rem',
          borderRadius: 'var(--radius-sm)',
          fontSize: '0.85rem',
          fontWeight: 700,
          color: 'var(--text-secondary)',
          letterSpacing: '0.15em',
          textTransform: 'uppercase',
          marginBottom: '2rem',
        }}>
          STAGE / PERFORMANCE FRONT
        </div>

        {loading ? (
          <div style={{ padding: '3rem 0', color: 'var(--text-secondary)' }}>
            Loading live seat layout...
          </div>
        ) : seats.length === 0 ? (
          <div style={{ padding: '3rem 0', color: 'var(--text-secondary)' }}>
            No seat data available for this event.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', alignItems: 'center' }}>
            {Object.keys(rowsMap).sort().map((rowName) => (
              <div key={rowName} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap', justifyContent: 'center' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 800, color: 'var(--text-muted)', width: '24px' }}>
                  {rowName}
                </span>
                {rowsMap[rowName].map((seat) => (
                  <SeatGridCell
                    key={seat.id}
                    id={seat.id}
                    row={seat.row}
                    seatNumber={seat.seat_number}
                    section={seat.section}
                    price={Number(seat.price)}
                    status={activeHold?.seat_ids?.includes(seat.id) ? 'LOCKED' : seat.status}
                    isSelected={selectedSeatIds.includes(seat.id)}
                    onClick={() => handleSeatClick(seat)}
                  />
                ))}
              </div>
            ))}
          </div>
        )}

        {/* Legend */}
        <div style={{ display: 'flex', gap: '1.5rem', justifyContent: 'center', marginTop: '2.5rem', fontSize: '0.85rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: 'var(--status-available)' }}></span>
            <span>Available</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: 'var(--accent-indigo)' }}></span>
            <span>Selected</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: 'var(--status-locked)' }}></span>
            <span>Locked / Held</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: 'var(--status-sold)' }}></span>
            <span>Sold</span>
          </div>
        </div>
      </div>

      {/* Reservation & Hold Action Panel */}
      {selectedSeatIds.length > 0 && (
        <div className="glass-card" style={{
          position: 'sticky',
          bottom: '1.5rem',
          zIndex: 90,
          background: 'rgba(15, 23, 42, 0.92)',
          backdropFilter: 'blur(16px)',
          border: '1px solid var(--accent-indigo)',
          display: 'flex',
          justify: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
        }}>
          <div>
            <div style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
              {selectedSeatIds.length} seat(s) selected
            </div>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-indigo)' }}>
              Total: ${selectedTotal.toFixed(2)}
            </div>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            {!activeHold ? (
              <button
                onClick={handleHoldSeats}
                className="btn btn-primary"
                disabled={holdLoading}
                style={{ padding: '0.75rem 1.5rem' }}
              >
                {holdLoading ? 'Acquiring Hold...' : 'Hold Selected Seats (5 min)'}
              </button>
            ) : (
              <button
                onClick={handleCheckout}
                className="btn btn-primary"
                disabled={checkoutLoading}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                }}
              >
                {checkoutLoading ? 'Processing Payment...' : 'Complete Checkout ($' + selectedTotal.toFixed(2) + ')'}
              </button>
            )}
          </div>
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
