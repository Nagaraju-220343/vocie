import { useEffect, useState, useCallback } from 'react';
import { getSocket } from '@/lib/socket/socket';

export interface RealtimeEventPayload {
  event: string;
  callId: string;
  sequence: number;
  payload: any;
}

export function useRealtime(room?: string) {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const socket = getSocket();

    const onConnect = () => setIsConnected(true);
    const onDisconnect = () => setIsConnected(false);

    socket.on('connect', onConnect);
    socket.on('disconnect', onDisconnect);

    if (!socket.connected) {
      socket.connect();
    } else {
      setIsConnected(true);
    }

    if (room) {
      if (room === 'restaurant:live-calls') {
        socket.emit('subscribe_live_calls', {});
      } else if (room.startsWith('call:')) {
        const callId = room.split(':')[1];
        socket.emit('join_call_room', { callId });
      }
    }

    return () => {
      socket.off('connect', onConnect);
      socket.off('disconnect', onDisconnect);
      
      if (room) {
        if (room === 'restaurant:live-calls') {
          socket.emit('unsubscribe_live_calls', {});
        } else if (room.startsWith('call:')) {
          const callId = room.split(':')[1];
          socket.emit('leave_call_room', { callId });
        }
      }
    };
  }, [room]);

  const useEvent = useCallback((eventName: string, callback: (data: RealtimeEventPayload) => void) => {
    useEffect(() => {
      const socket = getSocket();
      socket.on(eventName, callback);
      return () => {
        socket.off(eventName, callback);
      };
    }, [eventName, callback]);
  }, []);

  return { isConnected, useEvent };
}
