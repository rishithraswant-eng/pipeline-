import { create } from 'zustand'

export const useSessionStore = create((set) => ({
  systemStatus: { shadowmesh: 'offline', mirrortrap: 'offline', redis: 'offline' },
  wsConnected: false,
  sessionState: 'idle',
  sessionId: null,
  sessionStartTime: null,
  sessionEndTime: null,
  commands: [],
  commandCount: 0,
  profile: {
    expertise: { level: 'Script Kiddie', confidence: 0 },
    objective: { type: 'unknown', scores: [] },
    state: { type: 'calm', onset_seconds: 0 },
    attribution: []
  },
  nodes: [],
  edges: [],
  stats: {
    commands: 0,
    techniques: 0,
    dwell: 0,
    engagementScore: 0
  },
  iocs: { c2_ips: [], payloads: [], domains: [] },
  iciHistory: [],
  dossierStatus: 'idle',
  dossierData: null,
  
  // Actions
  setSystemStatus: (status) => set({ systemStatus: status }),
  setWsConnected: (connected) => set({ wsConnected: connected }),
  addCommand: (command) => set((state) => ({ commands: [...state.commands, command], commandCount: state.commandCount + 1 })),
  updateProfile: (profile) => set({ profile }),
  setSessionState: (state) => set({ sessionState: state }),
  setDossierReady: (data) => set({ dossierStatus: 'ready', dossierData: data }),
  resetSession: () => set({ sessionState: 'idle', sessionId: null, commands: [], commandCount: 0, stats: { commands: 0, techniques: 0, dwell: 0, engagementScore: 0 }, iciHistory: [] })
}))
