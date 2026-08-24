import { io } from 'socket.io-client';
import { useSessionStore } from '../store/sessionStore';

const SOCKET_URL = 'http://localhost:8000';
let socket = null;

export const connectSocket = () => {
    if (socket) return;

    socket = io(SOCKET_URL, {
        transports: ['websocket', 'polling'],
    });

    socket.on('connect', () => {
        console.log('Connected to WebSocket server');
        useSessionStore.getState().setWsConnected(true);
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from WebSocket server');
        useSessionStore.getState().setWsConnected(false);
    });

    // Event routing to Zustand
    socket.on('init_state', (data) => {
        useSessionStore.getState().setInitState(data);
    });

    socket.on('session_started', (data) => {
        useSessionStore.getState().startSession(data);
    });

    socket.on('command_received', (data) => {
        useSessionStore.getState().addCommand(data);
    });

    socket.on('profile_updated', (data) => {
        useSessionStore.getState().updateProfile(data);
    });

    socket.on('topology_mutated', (data) => {
        useSessionStore.getState().mutateTopology(data);
    });

    socket.on('dossier_ready', (data) => {
        useSessionStore.getState().setDossierReady(data);
    });
};

export const disconnectSocket = () => {
    if (socket) {
        socket.disconnect();
        socket = null;
    }
};

export const getSocket = () => socket;
