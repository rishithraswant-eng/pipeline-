import React from 'react';
import { useSessionStore } from '../store/sessionStore';
import { Download, X } from 'lucide-react';

const DossierModal = () => {
  const dossierStatus = useSessionStore((state) => state.dossierStatus);
  const dossierData = useSessionStore((state) => state.dossierData);
  const resetSession = useSessionStore((state) => state.resetSession);

  if (dossierStatus !== 'ready' || !dossierData) {
    return null;
  }

  const handleDownloadPdf = () => {
    const sessionId = dossierData?.session_id;
    if (!sessionId) return;
    const link = document.createElement('a');
    link.href = `http://localhost:8000/api/session/${sessionId}/dossier/pdf`;
    link.download = `PHANTASM_Dossier_${sessionId}.pdf`;
    link.click();
  };

  const handleClose = () => {
    resetSession();
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0, 0, 0, 0.7)',
      backdropFilter: 'blur(4px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 100
    }}>
      <div style={{
        background: 'var(--bg-elevated)',
        border: '1px solid var(--border-accent)',
        borderRadius: '8px',
        width: '600px',
        maxWidth: '90vw',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        boxShadow: 'var(--shadow-lg)'
      }}>
        {/* Header */}
        <div style={{
          padding: '24px',
          borderBottom: '1px solid var(--bg-border)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <div>
            <h2 style={{ margin: 0, fontSize: 'var(--text-lg)', color: 'var(--text-amber)' }}>
              Operator Dossier Ready
            </h2>
            <div style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)', marginTop: '4px', fontFamily: 'monospace' }}>
              SESSION: {dossierData.session_id}
            </div>
          </div>
          <button onClick={handleClose} style={{
            background: 'transparent',
            border: 'none',
            color: 'var(--text-muted)',
            cursor: 'pointer'
          }}>
            <X size={24} />
          </button>
        </div>

        {/* Content */}
        <div style={{ padding: '24px', overflowY: 'auto', flex: 1, color: 'var(--text-secondary)' }}>
          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ fontSize: 'var(--text-base)', color: 'var(--text-primary)', marginBottom: '8px' }}>Executive Summary</h3>
            <div style={{ 
              background: 'var(--bg-void)', 
              padding: '16px', 
              borderRadius: '6px', 
              border: '1px solid var(--bg-border)',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap'
            }}>
              {dossierData.narrative}
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div style={{ background: 'var(--bg-surface)', padding: '16px', borderRadius: '6px', border: '1px solid var(--bg-border)' }}>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Primary Objective</div>
              <div style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{dossierData.objective?.type?.toUpperCase() || 'UNKNOWN'}</div>
            </div>
            <div style={{ background: 'var(--bg-surface)', padding: '16px', borderRadius: '6px', border: '1px solid var(--bg-border)' }}>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Assessed Expertise</div>
              <div style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{dossierData.expertise?.level || 'Unknown'}</div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div style={{
          padding: '24px',
          borderTop: '1px solid var(--bg-border)',
          display: 'flex',
          justifyContent: 'flex-end',
          gap: '16px'
        }}>
          <button onClick={handleClose} style={{
            background: 'transparent',
            border: '1px solid var(--bg-border)',
            color: 'var(--text-primary)',
            padding: '8px 16px',
            borderRadius: '4px',
            cursor: 'pointer'
          }}>
            Close
          </button>
          <button onClick={handleDownloadPdf} style={{
            background: 'var(--accent-cyan)',
            color: '#000',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 600,
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Download size={16} />
            Download PDF
          </button>
        </div>
      </div>
    </div>
  );
};

export default DossierModal;
