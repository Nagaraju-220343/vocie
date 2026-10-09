import { io, Socket } from 'socket.io-client';

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:8000';

class SocketClient {
  private static instance: Socket | null = null;

  public static getInstance(): Socket {
    if (!SocketClient.instance) {
      SocketClient.instance = io(SOCKET_URL, {
        autoConnect: false, // Don't connect until needed
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
      });
    }
    return SocketClient.instance;
  }
}

export const getSocket = () => SocketClient.getInstance();
