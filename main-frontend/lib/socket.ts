// to help with returning customer instances. Null if mock.

// lib/socket.ts
import { io, Socket } from 'socket.io-client';

const MOCK = process.env.NEXT_PUBLIC_MOCK_API === 'true';
const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_IO_URL || '';

let socket: Socket | null = null;

export function getSocket() {
  if (MOCK) return null;
  if (!socket) {
    socket = io(SOCKET_URL || undefined, { transports: ['websocket'] });
  }
  return socket;
}
