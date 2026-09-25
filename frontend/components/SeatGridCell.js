'use client';

export default function SeatGridCell({
  id,
  row,
  seatNumber,
  section,
  price,
  status = 'AVAILABLE',
  isSelected = false,
  onClick,
}) {
  const isAvailable = status === 'AVAILABLE';
  const isLocked = status === 'LOCKED';
  const isSold = status === 'SOLD';

  let bg = 'var(--seat-available-bg)';
  let border = 'var(--seat-available-border)';
  let textColor = 'var(--seat-available-text)';
  let cursor = 'pointer';

  if (isSelected) {
    bg = 'var(--seat-selected-bg)';
    border = 'var(--seat-selected-border)';
    textColor = 'var(--seat-selected-text)';
  } else if (isLocked) {
    bg = 'var(--seat-locked-bg)';
    border = 'var(--seat-locked-border)';
    textColor = 'var(--seat-locked-text)';
    cursor = 'not-allowed';
  } else if (isSold) {
    bg = 'var(--seat-sold-bg)';
    border = 'var(--seat-sold-border)';
    textColor = 'var(--seat-sold-text)';
    cursor = 'not-allowed';
  }

  const handleClick = () => {
    if (isAvailable && onClick) {
      onClick({ id, row, seatNumber, section, price, status });
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={!isAvailable}
      title={`Row ${row}, Seat ${seatNumber} ($${price}) - ${isSelected ? 'Selected' : status}`}
      style={{
        width: '52px',
        height: '52px',
        borderRadius: 'var(--radius-sm)',
        background: bg,
        border: `1.5px solid ${border}`,
        color: textColor,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        cursor,
        fontWeight: 700,
        fontSize: '0.8rem',
        transition: 'var(--transition-fast)',
        boxShadow: isSelected ? 'var(--seat-selected-glow)' : 'none',
        position: 'relative',
        userSelect: 'none',
      }}
    >
      <span style={{ fontSize: '0.65rem', opacity: 0.8, lineHeight: 1 }}>
        {row}
      </span>
      <span style={{ fontSize: '0.85rem', lineHeight: 1.1 }}>
        {seatNumber}
      </span>
    </button>
  );
}
