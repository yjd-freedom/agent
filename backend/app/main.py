import asyncio
import json

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse

from .store import Session, sessions

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/sessions")
async def create_session():
    session = Session()
    sessions[session.id] = session
    return {"sessionId": session.id}


@app.get("/api/sessions/{session_id}/events")
async def session_events(session_id: str, after: int = Query(default=0, ge=0)):
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    async def events():
        cursor = after
        while True:
            for event in await session.read_after(cursor):
                cursor = event["seq"]
                yield f"id: {cursor}\nevent: {event['type']}\ndata: {json.dumps(event)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/api/demo-stream")
async def demo_stream():
    async def events():
        for seq in range(1, 6):
            yield f"id: {seq}\ndata: {json.dumps({'seq': seq})}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(events(), media_type="text/event-stream")
