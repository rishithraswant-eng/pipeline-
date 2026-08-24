import React, { useEffect, useState } from 'react';
import { useSessionStore } from '../store/sessionStore';

const StatusBar = () => {
  const sessionState = useSessionStore((state) => state.sessionState);
  const sessionId = useSessionStore((state) => state.sessionId);
  const sessionStartTime = useSessionStore((state) => state.sessionStartTime);
  const stats = useSessionStore((state) => state.stats);
  const dossierStatus = useSessionStore((state) => state.dossierStatus);
  
  const [elapsed, setElapsed] = useState('00:00:00');

  useEffect(() => {
    let interval;
    if (sessionState === 'active' && sessionStartTime) {
      // Parse the custom timestamp format "YYYYMMDDHHMMSS" if necessary, 
      // or assume it's something parseable if we fix backend.
      // Assuming sessionStartTime is a valid date string or timestamp for now.
      // The backend emits ts like "20260824161910", so let's handle that format:
      let startTimeMs;
      if (typeof sessionStartTime === 'string' && sessionStartTime.length === 14 && !sessionStartTime.includes('-')) {
        const y = sessionStartTime.substring(0,4);
        const m = sessionStartTime.substring(4,6);
        const d = sessionStartTime.substring(6,8);
        const h = sessionStartTime.substring(8,10);
        const min = sessionStartTime.substring(10,12);
        const s = sessionStartTime.substring(12,14);
        startTimeMs = new Date(`${y}-${m}-${d}T${h}:${min}:${s}Z`).getTime();
      } else {
        startTimeMs = new Date(sessionStartTime).getTime();
      }

      interval = setInterval(() => {
        const diff = Math.floor((Date.now() - startTimeMs) / 1000);
        if (diff >= 0) {
          const hrs = Math.floor(diff / 3600).toString().padStart(2, '0');
          const mins = Math.floor((diff % 3600) / 60).toString().padStart(2, '0');
          const secs = (diff % 60).toString().padStart(2, '0');
          setElapsed(`${hrs}:${mins}:${secs}`);
        }
      }, 1000);
    } else {
      setElapsed('00:00:00');
    }

    return () => clearInterval(interval);
  }, [sessionState, sessionStartTime]);

  const handleGenerateDossier = async () => {
    if (!sessionId) return;
    try {
      // This will trigger the backend to generate dossier and emit 'dossier_ready'
      await fetch(`http://localhost:8000/api/session/${sessionId}/dossier`);
    } catch (error) {
      console.error("Failed to generate dossier:", error);
    }
  };

  return (
    <div style={{
      height: '50px',
      zIndex: 10,
      background: 'rgba(255, 255, 255, 0.75)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      borderTop: '1px solid rgba(226, 232, 240, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      color: 'var(--text-muted)',
      fontSize: 'var(--text-sm)',
      boxShadow: '0 -2px 10px rgba(0, 0, 0, 0.03)'
    }}>
      <div style={{ display: 'flex', gap: '32px' }}>
        <div>
          <span style={{ marginRight: '8px' }}>SESSION TIME:</span>
          <span style={{ fontFamily: 'monospace', color: sessionState === 'active' ? 'var(--text-primary)' : 'inherit' }}>
            {elapsed}
          </span>
        </div>
        <div>
          <span style={{ marginRight: '8px' }}>COMMANDS:</span>
          <span style={{ fontFamily: 'monospace', color: 'var(--text-primary)' }}>{stats.totalCommands}</span>
        </div>
        <div>
          <span style={{ marginRight: '8px' }}>TECHNIQUES:</span>
          <span style={{ fontFamily: 'monospace', color: 'var(--text-primary)' }}>{stats.uniqueTechniques}</span>
        </div>
      </div>
      
      <div>
        <button 
          onClick={handleGenerateDossier}
          disabled={sessionState === 'idle' || dossierStatus === 'loading'}
          style={{
            background: 'transparent',
            color: (sessionState === 'idle' || dossierStatus === 'loading') ? 'var(--text-muted)' : 'var(--accent-blue)',
            border: 'none',
            padding: '6px 16px',
            borderRadius: '4px',
            cursor: (sessionState === 'idle' || dossierStatus === 'loading') ? 'not-allowed' : 'pointer',
            fontWeight: 700,
            fontSize: '12px',
            textTransform: 'uppercase'
          }}
        >
          Generate Dossier
        </button>
      </div>
    </div>
  );
};

export default StatusBar;
