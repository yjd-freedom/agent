import asyncio
import json
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from .agent import BUSY, run_agent
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


def get_session(session_id: str):
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail='Session not found')
    return session


@app.get('/api/sessions/{session_id}')
async def session_status(session_id: str):
    session = get_session(session_id)
    return {'sessionId': session.id, 'state': session.state}


class Message(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class Decision(BaseModel):
    decision: str
    prompt: str | None = Field(default=None, max_length=1000)


class FailureSetting(BaseModel):
    enabled: bool


@app.post('/api/sessions/{session_id}/messages')
async def send_message(session_id: str, message: Message):
    if not message.text.strip():
        raise HTTPException(status_code=422, detail='Message cannot be blank')
    session = get_session(session_id)
    async with session.condition:
        if session.state in BUSY:
            raise HTTPException(status_code=409, detail='Current operation is still running')
        turn_id = str(uuid4())
        session.turn_id = turn_id
        session.state = 'searching'
        session.confirmation_id = None
        session.emit('user_message', turn_id, {'text': message.text})
        session.emit('turn_started', turn_id, {'message': message.text})
        session.emit('tool_started', turn_id, {'tool': 'search', 'status': 'in_progress'})
        session.task = asyncio.create_task(run_agent(session, turn_id, message.text))
        return {'turnId': turn_id}


@app.post('/api/sessions/{session_id}/confirmations/{confirmation_id}')
async def confirm(session_id: str, confirmation_id: str, body: Decision):
    session = get_session(session_id)
    if body.decision not in {'approve', 'edit_approve', 'reject'}:
        raise HTTPException(status_code=422, detail='Invalid decision')
    if body.decision == 'edit_approve' and (not body.prompt or not body.prompt.strip()):
        raise HTTPException(status_code=422, detail='Prompt cannot be blank')
    async with session.condition:
        if session.confirmation_id != confirmation_id:
            raise HTTPException(status_code=404, detail='Confirmation not found')
        if session.state != 'waiting_confirmation' or session.confirmation.done():
            raise HTTPException(status_code=409, detail='Confirmation already resolved')
        original = next(e['data']['prompt'] for e in reversed(session.events) if e['type'] == 'confirmation_required')
        final = body.prompt if body.decision == 'edit_approve' else original
        session.emit('confirmation_resolved', session.turn_id, {'confirmationId': confirmation_id, 'decision': body.decision, 'finalPrompt': final if body.decision != 'reject' else None})
        session.confirmation.set_result((body.decision, final))
        return {'status': 'accepted'}


@app.post('/api/sessions/{session_id}/cancel')
async def cancel(session_id: str):
    session = get_session(session_id)
    async with session.condition:
        if session.state not in BUSY:
            raise HTTPException(status_code=409, detail='No active turn')
        if session.state in {'searching', 'generating_image'}:
            tool = 'search' if session.state == 'searching' else 'generate_image'
            session.emit('tool_finished', session.turn_id, {'tool': tool, 'status': 'cancelled'})
        session.state = 'cancelled'
        session.emit('turn_ended', session.turn_id, {'reason': 'cancelled'})
        session.task.cancel()
        return {'status': 'cancelled'}


@app.post('/api/sessions/{session_id}/debug/image-failure')
async def image_failure(session_id: str, body: FailureSetting):
    session = get_session(session_id)
    async with session.condition:
        session.fail_next = body.enabled
    return {'enabled': body.enabled}


@app.get("/api/sessions/{session_id}/events")
async def session_events(session_id: str, after: int = Query(default=0, ge=0)):
    session = sessions.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    async def events():
        cursor = after
        yield ': connected\n\n'
        while True:
            try:
                batch = await asyncio.wait_for(session.read_after(cursor), timeout=15)
            except asyncio.TimeoutError:
                yield ': heartbeat\n\n'
                continue
            for event in batch:
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
