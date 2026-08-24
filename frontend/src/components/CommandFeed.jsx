import React, { useEffect, useRef } from 'react';
import { useSessionStore } from '../store/sessionStore';

const CommandFeed = () => {
  const sessionState = useSessionStore((state) => state.sessionState);
  const commands = useSessionStore((state) => state.commands);
  const endOfMessagesRef = useRef(null);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [commands]);

  if (sessionState === 'idle') {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        <p>No active session. Waiting for command feed...</p>
      </div>
    );
  }

  const getExpertiseColor = (expertise) => {
    return 'var(--accent-blue)';
  };

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <h2 style={{ fontSize: 'var(--text-base)', margin: '0 0 16px 0', paddingBottom: '16px', borderBottom: '1px solid var(--bg-border)' }}>
        Command Feed
      </h2>
      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px', paddingRight: '8px' }}>
        {commands.length === 0 ? (
          <div style={{ color: 'var(--text-muted)', textAlign: 'center', marginTop: '24px' }}>
            Listening for commands...
          </div>
        ) : (
          commands.map((cmd, i) => (
            <div key={i} style={{ 
              background: 'rgba(255, 255, 255, 0.75)', 
              padding: '12px', 
              borderRadius: '10px', 
              border: '1px solid rgba(226, 232, 240, 0.8)',
              boxShadow: '0 4px 12px rgba(0, 0, 0, 0.02)',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: 'var(--accent-blue)', fontSize: '12px', fontFamily: 'monospace', fontWeight: 600 }}>
                  {new Date(cmd.timestamp).toLocaleTimeString()}
                </span>
                <span style={{ 
                  fontSize: '11px', 
                  padding: '2px 8px', 
                  borderRadius: '12px', 
                  background: 'var(--bg-blue-light)', 
                  border: `1px solid var(--border-blue-light)`,
                  color: 'var(--accent-blue)',
                  fontWeight: 600
                }}>
                  {cmd.expertise || 'Unknown'}
                </span>
              </div>
              <div style={{ fontFamily: 'monospace', color: 'var(--text-secondary)', wordBreak: 'break-all', fontWeight: 500 }}>
                &gt; {cmd.raw}
              </div>
              {cmd.techniques && cmd.techniques.length > 0 && (
                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                  {cmd.techniques.map(tech => (
                    <span key={tech} style={{ fontSize: '10px', background: 'var(--bg-blue-light)', padding: '2px 6px', borderRadius: '4px', color: 'var(--accent-blue)', fontWeight: 600, border: '1px solid var(--border-blue-light)' }}>
                      {tech}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))
        )}
        <div ref={endOfMessagesRef} />
      </div>
    </div>
  );
};

export default CommandFeed;
