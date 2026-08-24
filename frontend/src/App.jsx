import React, { useEffect } from 'react';
import TopBar from './components/TopBar';
import CommandFeed from './components/CommandFeed';
import NetworkGraph from './components/NetworkGraph';
import OperatorProfile from './components/OperatorProfile';
import StatusBar from './components/StatusBar';
import DossierModal from './components/DossierModal';
import { connectSocket, disconnectSocket } from './services/socket';

function App() {
  useEffect(() => {
    connectSocket();
    return () => {
      disconnectSocket();
    };
  }, []);

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100vh', 
      width: '100vw', 
      background: 'linear-gradient(135deg, #DDE4F5 0%, #EEF1FB 60%, #F5F0FC 100%)', 
      overflow: 'hidden',
      position: 'relative'
    }}>
      <TopBar />

      {/* Main Viewport Container */}
      <div style={{ 
        flex: 1, 
        position: 'relative', 
        display: 'flex', 
        overflow: 'hidden',
        padding: '12px 16px',
        gap: '16px'
      }}>
        {/* Background Network Graph Layer */}
        <div style={{ 
          position: 'absolute', 
          top: 0, 
          left: 0, 
          right: 0, 
          bottom: 0, 
          zIndex: 1 
        }}>
          <NetworkGraph />
        </div>

        {/* Floating Glassmorphism Left Panel (Command Feed) */}
        <div style={{ 
          width: '380px', 
          zIndex: 2, 
          background: 'rgba(255, 255, 255, 0.68)', 
          backdropFilter: 'blur(20px) saturate(180%)', 
          WebkitBackdropFilter: 'blur(20px) saturate(180%)',
          borderRadius: '16px', 
          border: '1px solid rgba(255, 255, 255, 0.85)', 
          boxShadow: '0 20px 40px -15px rgba(0, 9, 30, 0.08), 0 0 0 1px rgba(226, 232, 240, 0.6)', 
          padding: '20px', 
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          <CommandFeed />
        </div>

        {/* Transparent Center Area for Interactive Network Graph */}
        <div style={{ flex: 1, zIndex: 2, pointerEvents: 'none' }} />

        {/* Floating Glassmorphism Right Panel (Operator Profile) */}
        <div style={{ 
          width: '360px', 
          zIndex: 2, 
          background: 'rgba(255, 255, 255, 0.68)', 
          backdropFilter: 'blur(20px) saturate(180%)', 
          WebkitBackdropFilter: 'blur(20px) saturate(180%)',
          borderRadius: '16px', 
          border: '1px solid rgba(255, 255, 255, 0.85)', 
          boxShadow: '0 20px 40px -15px rgba(0, 9, 30, 0.08), 0 0 0 1px rgba(226, 232, 240, 0.6)', 
          padding: '20px', 
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          <OperatorProfile />
        </div>
      </div>

      <StatusBar />
      
      <DossierModal />
    </div>
  )
}

export default App;
