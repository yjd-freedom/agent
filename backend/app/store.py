import asyncio
from datetime import datetime, timezone
from uuid import uuid4


class Session:
    def __init__(self):
        self.id = str(uuid4())
        self.condition = asyncio.Condition()
        self.events = []

    async def publish(self, event_type: str, turn_id: str, data: dict):
        async with self.condition:
            event = {
                "seq": len(self.events) + 1,
                "type": event_type,
                "sessionId": self.id,
                "turnId": turn_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": data,
            }
            self.events.append(event)
            self.condition.notify_all()
            return event

    async def read_after(self, seq: int):
        async with self.condition:
            while len(self.events) <= seq:
                await self.condition.wait()
            return self.events[seq:].copy()


sessions: dict[str, Session] = {}
