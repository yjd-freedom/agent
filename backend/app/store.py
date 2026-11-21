import asyncio
from datetime import datetime, timezone
from uuid import uuid4


class Session:
    def __init__(self):
        self.id = str(uuid4())
        self.condition = asyncio.Condition()
        self.events = []
        self.state = 'idle'
        self.turn_id = None
        self.task = None
        self.confirmation_id = None
        self.confirmation = None
        self.fail_next = False

    def emit(self, event_type: str, turn_id: str, data: dict):
        event = {
            'seq': len(self.events) + 1, 'type': event_type,
            'sessionId': self.id, 'turnId': turn_id,
            'timestamp': datetime.now(timezone.utc).isoformat(), 'data': data,
        }
        self.events.append(event)
        self.condition.notify_all()
        return event

    async def publish(self, event_type: str, turn_id: str, data: dict):
        async with self.condition:
            return self.emit(event_type, turn_id, data)

    async def read_after(self, seq: int):
        async with self.condition:
            while len(self.events) <= seq:
                await self.condition.wait()
            return self.events[seq:].copy()


sessions: dict[str, Session] = {}
