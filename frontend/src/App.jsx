import React from 'react';

function App() {
  return (
    <div style={{ display: 'grid', gridTemplateRows: '56px 1fr 80px', gridTemplateColumns: '380px 1fr 360px', height: '100vh', width: '100vw', background: 'var(--bg-void)', gap: '0' }}>
      {/* Header Bar */}
      <div style={{ gridColumn: '1 / 4', background: 'var(--bg-surface)', borderBottom: '1px solid var(--bg-border)', display: 'flex', alignItems: 'center', padding: '0 24px' }}>
        <h1 style={{ fontSize: 'var(--text-lg)', margin: 0 }}>PHANTASM</h1>
      </div>

      {/* Left Panel */}
      <div style={{ background: 'var(--bg-surface)', borderRight: '1px solid var(--bg-border)', padding: 'var(--space-6)' }}>
        <h2>Command Feed</h2>
      </div>

      {/* Center Panel */}
      <div style={{ padding: 'var(--space-6)' }}>
        <h2>Network Graph</h2>
      </div>

      {/* Right Panel */}
      <div style={{ background: 'var(--bg-surface)', borderLeft: '1px solid var(--bg-border)', padding: 'var(--space-6)' }}>
        <h2>Operator Profile</h2>
      </div>

      {/* Bottom Bar */}
      <div style={{ gridColumn: '1 / 4', background: 'var(--bg-surface)', borderTop: '1px solid var(--bg-border)', display: 'flex', alignItems: 'center', padding: '0 24px' }}>
        <span>Status</span>
      </div>
    </div>
  )
}

export default App;
