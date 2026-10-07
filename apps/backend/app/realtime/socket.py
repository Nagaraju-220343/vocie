import socketio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Create the Socket.IO asynchronous server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

class RealtimeEventPublisher:
    def __init__(self, sio_instance: socketio.AsyncServer):
        self.sio = sio_instance

    async def publish(self, event_type: str, call_id: str, sequence: int, payload: Dict[str, Any]):
        """
        Publish a normalized business event to the appropriate Socket.IO rooms.
        """
        event_data = {
            "event": event_type,
            "callId": call_id,
            "sequence": sequence,
            "payload": payload
        }
        
        # Publish to specific call room
        room_name = f"call:{call_id}"
        logger.debug(f"Publishing {event_type} to room {room_name}")
        await self.sio.emit(event_type, event_data, room=room_name)
        
        # Also publish to the global live-calls channel if appropriate
        await self.sio.emit(event_type, event_data, room="restaurant:live-calls")

# Global publisher instance
publisher = RealtimeEventPublisher(sio)

@sio.event
async def connect(sid, environ):
    logger.info(f"Socket.IO client connected: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"Socket.IO client disconnected: {sid}")

@sio.event
async def join_call_room(sid, data):
    call_id = data.get("callId")
    if call_id:
        room = f"call:{call_id}"
        await sio.enter_room(sid, room)
        logger.info(f"Client {sid} joined room {room}")

@sio.event
async def leave_call_room(sid, data):
    call_id = data.get("callId")
    if call_id:
        room = f"call:{call_id}"
        await sio.leave_room(sid, room)
        logger.info(f"Client {sid} left room {room}")

@sio.event
async def subscribe_live_calls(sid, data):
    await sio.enter_room(sid, "restaurant:live-calls")
    logger.info(f"Client {sid} subscribed to live calls")

@sio.event
async def unsubscribe_live_calls(sid, data):
    await sio.leave_room(sid, "restaurant:live-calls")
    logger.info(f"Client {sid} unsubscribed from live calls")
