'use client';

import { useState } from 'react';
import SeatGridCell from '@/components/SeatGridCell';
import CountdownTimer from '@/components/CountdownTimer';
import Toast from '@/components/Toast';

export default function EventDetailPage({ params }) {
  const eventId = params?.id || '1';
  const [selectedSeatIds, setSelectedSeatIds] = useState([]);
  const [toastMessage, setToastMessage] = useState(null);
  const [toastType, setToastType] = useState('info');

  const handleSeatClick = (seat) => {
    setSelectedSeatIds((prev) =>
      prev.includes(seat.id) ? prev.filter((id) => id !== seat.id) : [...prev, seat.id]
    );
  };

  return (
    <div className="container">
      {/* Event Header & Controls */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 900, marginBottom: '0.4rem' }}>
            Event Seat Reservation
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>
            Event ID #{eventId} • Click available seats to select
          </p>
        </div>

        <CountdownTimer initialSeconds={300} onExpire={() => setToastMessage('Hold lease expired!')} />
      </div>

      {/* Seat Map Grid Scaffold Demo */}
      <div className="glass-card" style={{ marginBottom: '2rem', textAlign: 'center' }}>
        <h3 style={{ fontSize: '1rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '1.5rem' }}>
          STAGE / STAGE FRONT
        </h3>

        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap', maxWidth: '600px', margin: '0 auto' }}>
          <SeatGridCell id={1} row="A" seatNumber={1} section="A" price={150} status="AVAILABLE" isSelected={selectedSeatIds.includes(1)} onClick={handleSeatClick} />
          <SeatGridCell id={2} row="A" seatNumber={2} section="A" price={150} status="AVAILABLE" isSelected={selectedSeatIds.includes(2)} onClick={handleSeatClick} />
          <SeatGridCell id={3} row="A" seatNumber={3} section="A" price={150} status="LOCKED" />
          <SeatGridCell id={4} row="A" seatNumber={4} section="A" price={150} status="SOLD" />
        </div>
      </div>

      {Toast && toastMessage && (
        <Toast message={toastMessage} type={toastType} onClose={() => setToastMessage(null)} />
      )}
    </div>
  );
}
