'use client';

interface ResultOverlayProps {
  victory: boolean;
  airportName: string;
  earnedMoney: number;
  onBack: () => void;
  onRetry: () => void;
}

const overlayStyle: React.CSSProperties = {
  position: 'fixed',
  inset: 0,
  zIndex: 50,
  background: 'rgba(0,0,0,0.85)',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  color: '#fff',
  gap: '1rem',
};

const headingStyle: React.CSSProperties = {
  fontSize: '3rem',
  fontWeight: 700,
  margin: 0,
};

const subtextStyle: React.CSSProperties = {
  fontSize: '1.25rem',
  margin: 0,
  opacity: 0.85,
};

const btnStyle: React.CSSProperties = {
  background: '#fff',
  color: '#111',
  border: 'none',
  borderRadius: '8px',
  padding: '0.75rem 1.75rem',
  fontSize: '1rem',
  fontWeight: 600,
  cursor: 'pointer',
};

export default function ResultOverlay({
  victory,
  airportName,
  earnedMoney,
  onBack,
  onRetry,
}: ResultOverlayProps) {
  if (victory) {
    return (
      <div style={overlayStyle}>
        <h1 style={headingStyle}>Victory!</h1>
        <p style={subtextStyle}>{airportName}</p>
        <p style={subtextStyle}>+${(earnedMoney ?? 0).toLocaleString()} earned</p>
        <button style={btnStyle} onClick={onBack}>
          Back to Map
        </button>
      </div>
    );
  }

  return (
    <div style={overlayStyle}>
      <h1 style={headingStyle}>Mission Failed</h1>
      <p style={subtextStyle}>Your battery ran out</p>
      <div style={{ display: 'flex', gap: '1rem' }}>
        <button style={btnStyle} onClick={onRetry}>
          Try Again
        </button>
        <button style={btnStyle} onClick={onBack}>
          Back to Map
        </button>
      </div>
    </div>
  );
}
