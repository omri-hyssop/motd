import { useEffect, useMemo, useState } from 'react';

const colors = ['#ff6b6b', '#f7b731', '#4cd137', '#00a8ff', '#9c88ff', '#ff9ff3'];

const Confetti = ({ active }) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    if (!active) return;
    setMounted(true);
    const t = setTimeout(() => setMounted(false), 4500);
    return () => clearTimeout(t);
  }, [active]);

  const pieces = useMemo(() => {
    return Array.from({ length: 70 }).map((_, idx) => {
      const left = Math.random() * 100;
      const delay = Math.random() * 800;
      const duration = 2500 + Math.random() * 2000;
      const size = 6 + Math.random() * 8;
      const rotate = Math.random() * 360;
      const color = colors[idx % colors.length];
      return { idx, left, delay, duration, size, rotate, color };
    });
  }, [mounted]);

  if (!mounted) return null;

  return (
    <div className="pointer-events-none fixed inset-0 z-40 overflow-hidden">
      <style>
        {`
          @keyframes motd-confetti-fall {
            0% { transform: translate3d(0,-10vh,0) rotate(0deg); opacity: 1; }
            100% { transform: translate3d(0,110vh,0) rotate(720deg); opacity: 0.9; }
          }
        `}
      </style>
      {pieces.map((p) => (
        <div
          key={p.idx}
          style={{
            position: 'absolute',
            top: '-10vh',
            left: `${p.left}%`,
            width: `${p.size}px`,
            height: `${Math.max(6, p.size * 0.6)}px`,
            backgroundColor: p.color,
            transform: `rotate(${p.rotate}deg)`,
            borderRadius: '2px',
            animation: `motd-confetti-fall ${p.duration}ms linear ${p.delay}ms 1`,
          }}
        />
      ))}
    </div>
  );
};

export default Confetti;

