import { io } from 'socket.io-client';
import { useSessionStore } from '../store/sessionStore';

const URL = process.env.NODE_ENV === 'production' ? undefined : 'http://localhost:8000';

export const socket = io(URL, {
  autoConnect: false
});

export const connectSocket = () => {
  socket.connect();
};

socket.on('connect', () => {
  useSessionStore.getState().setWsConnected(true);
});

socket.on('disconnect', () => {
  useSessionStore.getState().setWsConnected(false);
});
