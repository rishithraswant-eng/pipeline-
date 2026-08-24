import React from 'react';
import { useSessionStore } from '../store/sessionStore';
import { Activity, Database, Shield } from 'lucide-react';

const TopBar = () => {
  const sessionId = useSessionStore((state) => state.sessionId);
  const systemStatus = useSessionStore((state) => state.systemStatus);
  const wsConnected = useSessionStore((state) => state.wsConnected);

  const getStatusColor = (status) => {
    if (status === 'online') return 'var(--accent-green)';
    if (status === 'offline') return 'var(--accent-red)';
    return 'var(--text-muted)';
  };

  const StatusDot = ({ status }) => {
    let color = 'orange'; // default amber for unknown
    if (status === 'online' || status === true) color = 'var(--status-active)';
    if (status === 'offline' || status === false) color = 'var(--status-critical)';
    
    return (
      <div style={{ 
        width: '8px', 
        height: '8px', 
        borderRadius: '50%', 
        background: color,
        boxShadow: (status === 'online' || status === true) ? `0 0 8px ${color}` : 'none'
      }} />
    );
  };

  return (
    <div style={{
      height: '56px',
      zIndex: 10,
      background: 'rgba(255, 255, 255, 0.75)',
      backdropFilter: 'blur(12px)',
      WebkitBackdropFilter: 'blur(12px)',
      borderBottom: '1px solid rgba(226, 232, 240, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      boxShadow: '0 2px 10px rgba(0, 0, 0, 0.03)'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <img 
          src="/logo.png" 
          alt="Phantasm Logo" 
          style={{ 
            height: '40px', 
            objectFit: 'contain',
            mixBlendMode: 'multiply'
          }} 
        />
        <h1 style={{ fontSize: 'var(--text-lg)', margin: 0, fontWeight: 600, letterSpacing: '1px' }}>
          PHANTASM
        </h1>
        {sessionId && (
          <div style={{ background: 'var(--bg-blue-light)', padding: '4px 12px', borderRadius: '4px', border: '1px solid var(--border-blue-light)', fontFamily: 'monospace', color: 'var(--accent-blue)', fontWeight: 600 }}>
            SESSION: {sessionId}
          </div>
        )}
      </div>

      <div style={{ display: 'flex', gap: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Shield size={16} color={getStatusColor(systemStatus.shadowmesh)} />
          <StatusDot status={systemStatus.shadowmesh} />
          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>ShadowMesh</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Activity size={16} color={getStatusColor(systemStatus.mirrortrap)} />
          <StatusDot status={systemStatus.mirrortrap} />
          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>MirrorTrap</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Database size={16} color={getStatusColor(systemStatus.redis)} />
          <StatusDot status={systemStatus.redis} />
          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>Redis</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderLeft: '1px solid var(--bg-border)', paddingLeft: '24px' }}>
          <StatusDot status={wsConnected} />
          <span style={{ fontSize: 'var(--text-sm)', color: 'var(--text-muted)' }}>WS</span>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
