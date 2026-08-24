import React from 'react';
import { useSessionStore } from '../store/sessionStore';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

const OperatorProfile = () => {
  const sessionState = useSessionStore((state) => state.sessionState);
  const profile = useSessionStore((state) => state.profile);
  const iciHistory = useSessionStore((state) => state.iciHistory);

  if (sessionState === 'idle') {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        <p>No active session. Waiting for operator profile...</p>
      </div>
    );
  }

  const getExpertiseColor = (expertise) => {
    return 'var(--text-primary)';
  };

  const getGaugeColor = (score) => {
    if (score < 40) return 'var(--accent-green)';
    if (score < 70) return 'var(--accent-orange)';
    return 'var(--accent-red)';
  };

  const formattedIciData = iciHistory.map((d, i) => ({
    name: i,
    ici: (d.ici_ms / 1000).toFixed(1)
  }));

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: '24px', overflowY: 'auto', paddingRight: '8px' }}>
      <h2 style={{ fontSize: 'var(--text-base)', margin: '0', paddingBottom: '16px', borderBottom: '1px solid var(--bg-border)' }}>
        Operator Profile
      </h2>

      {/* Overview Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
        <div style={{ background: 'rgba(255, 255, 255, 0.65)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(226, 232, 240, 0.8)', boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>Expertise Level</div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: getExpertiseColor(profile.expertise_level) }}>
            {profile.expertise_level}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Confidence: {Math.round(profile.expertise_confidence * 100)}%
          </div>
        </div>
        
        <div style={{ background: 'rgba(255, 255, 255, 0.65)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(226, 232, 240, 0.8)', boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>State</div>
          <div style={{ fontSize: '18px', fontWeight: 600, color: 'var(--text-primary)' }}>
            {profile.operational_state.toUpperCase()}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
            Objective: {profile.primary_objective}
          </div>
        </div>
      </div>

      {/* Semi-Circle Engagement Score Gauge */}
      <div style={{ 
        background: 'rgba(255, 255, 255, 0.65)', 
        padding: '16px 20px', 
        borderRadius: '12px', 
        border: '1px solid rgba(226, 232, 240, 0.8)', 
        boxShadow: '0 4px 12px rgba(0,0,0,0.02)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        <div style={{ width: '100%', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px', textAlign: 'left' }}>
          Engagement Score
        </div>

        <div style={{ position: 'relative', width: '180px', height: '100px', display: 'flex', justifyContent: 'center', alignItems: 'flex-end' }}>
          <svg width="180" height="105" viewBox="0 0 180 105">
            <defs>
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#60A5FA" />
                <stop offset="50%" stopColor="#3B82F6" />
                <stop offset="100%" stopColor="#8B5CF6" />
              </linearGradient>
              <filter id="gaugeGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="0" dy="2" stdDeviation="4" floodColor="#3B82F6" floodOpacity="0.25" />
              </filter>
            </defs>

            {/* Background Arc */}
            <path
              d="M 20 90 A 70 70 0 0 1 160 90"
              fill="none"
              stroke="rgba(226, 232, 240, 0.7)"
              strokeWidth="12"
              strokeLinecap="round"
            />

            {/* Value Progress Arc */}
            <path
              d="M 20 90 A 70 70 0 0 1 160 90"
              fill="none"
              stroke="url(#gaugeGradient)"
              strokeWidth="12"
              strokeLinecap="round"
              strokeDasharray="219.91"
              strokeDashoffset={219.91 * (1 - Math.min(100, Math.max(0, profile.engagement_score)) / 100)}
              filter="url(#gaugeGlow)"
              style={{ transition: 'stroke-dashoffset 0.8s cubic-bezier(0.34, 1.56, 0.64, 1)' }}
            />

            {/* Center Score Text */}
            <text x="90" y="72" textAnchor="middle" fontSize="26" fontWeight="700" fill="#0F172A" fontFamily="var(--font-mono)">
              {profile.engagement_score.toFixed(1)}
            </text>
            <text x="90" y="90" textAnchor="middle" fontSize="11" fontWeight="600" fill="var(--text-muted)" letterSpacing="0.5px">
              / 100 SCORE
            </text>
          </svg>
        </div>
      </div>

      {/* ICI Timeline */}
      <div style={{ background: 'rgba(255, 255, 255, 0.65)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(226, 232, 240, 0.8)', boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '16px' }}>Inter-Command Interval (s)</div>
        <div style={{ height: '120px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={formattedIciData}>
              <XAxis dataKey="name" hide />
              <YAxis stroke="var(--text-muted)" fontSize={10} width={30} />
              <Tooltip 
                contentStyle={{ background: 'rgba(255, 255, 255, 0.95)', border: '1px solid rgba(226, 232, 240, 0.8)', borderRadius: '6px' }}
                itemStyle={{ color: 'var(--text-primary)' }}
              />
              <Line type="monotone" dataKey="ici" stroke="var(--accent-blue)" strokeWidth={2} dot={false} isAnimationActive={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
      
      {/* Techniques Summary */}
      <div style={{ background: 'rgba(255, 255, 255, 0.65)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(226, 232, 240, 0.8)', boxShadow: '0 4px 12px rgba(0,0,0,0.02)' }}>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>Unique Techniques Used</div>
        <div style={{ fontSize: '24px', fontWeight: 600 }}>{profile.unique_techniques}</div>
      </div>
    </div>
  );
};

export default OperatorProfile;
