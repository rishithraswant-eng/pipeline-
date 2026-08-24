import { create } from 'zustand'

export const useSessionStore = create((set) => ({
  systemStatus: { shadowmesh: 'offline', mirrortrap: 'offline', redis: 'offline' },
  wsConnected: false,
  
  sessionState: 'idle',
  sessionId: null,
  sessionStartTime: null,
  
  commands: [],
  
  profile: {
    expertise_level: 'Unknown',
    expertise_confidence: 0,
    primary_objective: 'unknown',
    operational_state: 'calm',
    engagement_score: 0,
    unique_techniques: 0
  },
  
  topology: { nodes: [], edges: [], subnets: [] },
  stats: {
    totalCommands: 0,
    uniqueTechniques: 0
  },
  iciHistory: [], // stores { seq, ici_ms }
  
  dossierStatus: 'idle',
  dossierData: null,
  
  // Actions
  setWsConnected: (connected) => set({ wsConnected: connected }),
  
  setInitState: (data) => set({
    topology: data.topology || { nodes: [], edges: [], subnets: [] },
    systemStatus: data.system_status || { shadowmesh: 'offline', mirrortrap: 'offline', redis: 'offline' }
  }),
  
  startSession: (data) => set({
    sessionState: 'active',
    sessionId: data.session_id,
    sessionStartTime: data.created_at, // Consider converting to Date object
    commands: [],
    profile: {
      expertise_level: 'Unknown',
      expertise_confidence: 0,
      primary_objective: 'unknown',
      operational_state: 'calm',
      engagement_score: 0,
      unique_techniques: 0
    },
    stats: {
      totalCommands: 0,
      uniqueTechniques: 0
    },
    iciHistory: [],
    dossierStatus: 'idle',
    dossierData: null
  }),
  
  addCommand: (data) => set((state) => ({
    commands: [...state.commands, {
      seq: data.command_seq,
      raw: data.raw_command,
      techniques: data.technique_ids || [],
      expertise: data.expertise_level,
      timestamp: data.timestamp_ms
    }],
    stats: {
      ...state.stats,
      totalCommands: state.stats.totalCommands + 1
    }
  })),
  
  updateProfile: (data) => set((state) => {
    const newIciHistory = data.ici_ms !== undefined ? 
      [...state.iciHistory, { time: Date.now(), ici_ms: data.ici_ms }].slice(-20) : // Keep last 20
      state.iciHistory;
      
    return {
      profile: {
        expertise_level: data.expertise_level,
        expertise_confidence: data.expertise_confidence,
        primary_objective: data.primary_objective,
        operational_state: data.operational_state,
        engagement_score: data.engagement_score,
        unique_techniques: data.unique_techniques
      },
      stats: {
        ...state.stats,
        uniqueTechniques: data.unique_techniques
      },
      iciHistory: newIciHistory
    };
  }),
  
  mutateTopology: (data) => set((state) => ({
    // Topology mutation logic will be fully implemented when backend supports it
    // For now we could just track mutation events or update node count if needed.
  })),
  
  setDossierReady: (data) => set({ 
    dossierStatus: 'ready', 
    dossierData: data 
  }),
  
  resetSession: () => set({ 
    sessionState: 'idle', 
    sessionId: null, 
    commands: [],
    stats: { totalCommands: 0, uniqueTechniques: 0 }, 
    iciHistory: [],
    dossierStatus: 'idle'
  })
}))
