# Change log

### 修改日期：2026-11-21

- **修改文件**：`frontend/vite.config.ts`
- **修改的原因**：本机 8000 端口已被占用。
- **修改前功能**：开发代理连接 8000 端口。
- **修改后功能**：开发代理连接 18000 端口。

#### 1. 修改前的代码（含行号）
```ts
// 第 6 行
  server: { proxy: { '/health': 'http://127.0.0.1:8000', '/api': 'http://127.0.0.1:8000' } },
```

#### 2. 修改后的代码（含行号）
```ts
// 第 6 行
  server: { proxy: { '/health': 'http://127.0.0.1:18000', '/api': 'http://127.0.0.1:18000' } },
```

### ?????2026-11-21

- **????**?`backend/app/main.py`
- **?????**???????????????
- **?????**???????
- **?????**???????????????

#### 1. ???????????
```text
// ?????
```

#### 2. ???????????
```text
// ? 1 ? ~ ? 8 ?
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}
```

### ?????2026-11-21

- **????**?`backend/requirements.txt`
- **?????**???????????????
- **?????**???????
- **?????**???????????????

#### 1. ???????????
```text
// ?????
```

#### 2. ???????????
```text
// ? 1 ? ~ ? 2 ?
fastapi>=0.115,<1
uvicorn[standard]>=0.30,<1
```

### ?????2026-11-21

- **????**?`frontend/package.json`
- **?????**???????????????
- **?????**???????
- **?????**???????????????

#### 1. ???????????
```text
// ?????
```

#### 2. ???????????
```text
// ? 1 ? ~ ? 9 ?
{
  "name": "streaming-agent-chat",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": { "dev": "vite --host 127.0.0.1", "build": "tsc -b && vite build" },
  "dependencies": { "react": "^19.0.0", "react-dom": "^19.0.0" },
  "devDependencies": { "@types/react": "^19.0.0", "@types/react-dom": "^19.0.0", "@vitejs/plugin-react": "^4.3.4", "typescript": "^5.7.2", "vite": "^6.0.0" }
}
```

### ?????2026-11-21

- **????**?`frontend/tsconfig.json`
- **?????**???????????????
- **?????**???????
- **?????**???????????????

#### 1. ???????????
```text
// ?????
```

#### 2. ???????????
```text
// ? 1 ? ~ ? 1 ?
{"compilerOptions":{"target":"ES2022","module":"ESNext","moduleResolution":"Bundler","jsx":"react-jsx","strict":true,"noEmit":true,"skipLibCheck":true},"include":["src","vite.config.ts"]}
```

### ?????2026-11-21

- **????**?`frontend/vite.config.ts`
- **?????**???????????????
- **?????**???????
- **?????**???????????????

#### 1. ???????????
```text
// ?????
```

#### 2. ???????????
```text
// ? 1 ? ~ ? 7 ?
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/health': 'http://127.0.0.1:8000', '/api': 'http://127.0.0.1:8000' } },
});
```

### ?????2026-11-21

- **????**?`frontend/index.html`
- **?????**???????????????
- **?????**???????
- **?????**???????????????

#### 1. ???????????
```text
// ?????
```

#### 2. ???????????
```text
// ? 1 ? ~ ? 2 ?
<!doctype html>
<html lang="en"><head><meta charset="UTF-8" /><meta name="viewport" content="width=device-width, initial-scale=1.0" /><title>Streaming Agent Chat</title></head><body><div id="root"></div><script type="module" src="/src/main.tsx"></script></body></html>
```

### ?????2026-11-21

- **????**?`frontend/src/main.tsx`
- **?????**???????????????
- **?????**???????
- **?????**???????????????

#### 1. ???????????
```text
// ?????
```

#### 2. ???????????
```text
// ? 1 ? ~ ? 15 ?
import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  const [health, setHealth] = useState('checking');
  useEffect(() => {
    fetch('/health').then(response => {
      if (!response.ok) throw new Error('Health check failed');
      return response.json();
    }).then(result => setHealth(result.status)).catch(() => setHealth('unavailable'));
  }, []);
  return <main><h1>Streaming Agent Chat</h1><p>Backend: {health}</p></main>;
}

createRoot(document.getElementById('root')!).render(<App />);
```

### ?????2026-11-21

- **????**?`.gitignore`
- **?????**???????????????
- **?????**???????
- **?????**???????????????

#### 1. ???????????
```text
// ?????
```

#### 2. ???????????
```text
// ? 1 ? ~ ? 7 ?
test_code/
frontend/node_modules/
frontend/dist/
*.tsbuildinfo
__pycache__/
.env
agent_streaming_confirmation_requirements.md
```

### ?????2026-11-21

- **????**?`backend/app/main.py`
- **?????**?????? SSE ????????
- **?????**?????????
- **?????**?????????????????????

#### 1. ???????????
```text
// ? 1 ? ~ ? 8 ?
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}
```

#### 2. ???????????
```text
// ? 1 ? ~ ? 22 ?
import asyncio
import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/demo-stream")
async def demo_stream():
    async def events():
        for seq in range(1, 6):
            yield f"id: {seq}\ndata: {json.dumps({'seq': seq})}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(events(), media_type="text/event-stream")
```

### ?????2026-11-21

- **????**?`frontend/src/main.tsx`
- **?????**?????? SSE ????????
- **?????**?????????
- **?????**?????????????????????

#### 1. ???????????
```text
// ? 1 ? ~ ? 15 ?
import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  const [health, setHealth] = useState('checking');
  useEffect(() => {
    fetch('/health').then(response => {
      if (!response.ok) throw new Error('Health check failed');
      return response.json();
    }).then(result => setHealth(result.status)).catch(() => setHealth('unavailable'));
  }, []);
  return <main><h1>Streaming Agent Chat</h1><p>Backend: {health}</p></main>;
}

createRoot(document.getElementById('root')!).render(<App />);
```

#### 2. ???????????
```text
// ? 1 ? ~ ? 25 ?
import { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';

function App() {
  const [health, setHealth] = useState('checking');
  const [events, setEvents] = useState<number[]>([]);
  useEffect(() => {
    fetch('/health').then(response => {
      if (!response.ok) throw new Error('Health check failed');
      return response.json();
    }).then(result => setHealth(result.status)).catch(() => setHealth('unavailable'));
  }, []);
  useEffect(() => {
    const source = new EventSource('/api/demo-stream');
    source.onmessage = event => {
      const { seq } = JSON.parse(event.data) as { seq: number };
      setEvents(previous => previous.includes(seq) ? previous : [...previous, seq]);
      if (seq === 5) source.close();
    };
    return () => source.close();
  }, []);
  return <main><h1>Streaming Agent Chat</h1><p>Backend: {health}</p><p>Stream: {events.join(', ') || 'waiting'}</p></main>;
}

createRoot(document.getElementById('root')!).render(<App />);
```

### ?????2026-11-21

- **????**?`backend/app/svg.py`
- **?????**?????????? Prompt ? SVG?
- **?????**?????????????
- **?????**??????????????? SVG?

#### 1. ???????????
```text
// ?????
```

#### 2. ???????????
```python
// ? 1 ? ~ ? 17 ?
import html
import re


def make_svg(text: str, color: str = "#315a81") -> str:
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        raise ValueError("Color must be a six-digit hex value")
    escaped = html.escape(text, quote=True)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="400" '
        'viewBox="0 0 800 400">'
        f'<rect width="800" height="400" fill="{color}"/>'
        '<foreignObject x="40" y="40" width="720" height="320">'
        '<div xmlns="http://www.w3.org/1999/xhtml" '
        'style="color:white;font:24px sans-serif;overflow-wrap:anywhere">'
        f'{escaped}</div></foreignObject></svg>'
    )
```

### ?????2026-11-21

- **????**?`backend/app/store.py`
- **?????**???????????????
- **?????**????????????
- **?????**???????????????????

#### 1. ???????????
```python
// ? 1 ? ~ ? 1 ?
// ?????
```

#### 2. ???????????
```python
// ? 1 ? ~ ? 33 ?
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
```

### ?????2026-11-21

- **????**?`backend/app/main.py`
- **?????**???????????????
- **?????**????????????
- **?????**???????????????????

#### 1. ???????????
```python
// ? 1 ? ~ ? 22 ?
import asyncio
import json

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/demo-stream")
async def demo_stream():
    async def events():
        for seq in range(1, 6):
            yield f"id: {seq}\ndata: {json.dumps({'seq': seq})}\n\n"
            await asyncio.sleep(1)

    return StreamingResponse(events(), media_type="text/event-stream")
```

#### 2. ???????????
```python
// ? 1 ? ~ ? 47 ?
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
```

### ?????2026-11-21

- **????**?`backend/app/store.py`
- **?????**????? Agent????????????
- **?????**??????????????
- **?????**???????????????

#### 1. ???????????
```python
// ? 1 ? ~ ? 33 ?
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
```

#### 2. ???????????
```python
// ? 1 ? ~ ? 39 ?
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
```

### ?????2026-11-21

- **????**?`backend/app/agent.py`
- **?????**????? Agent????????????
- **?????**??????????????
- **?????**???????????????

#### 1. ???????????
```python
// ? 1 ? ~ ? 1 ?
// ?????
```

#### 2. ???????????
```python
// ? 1 ? ~ ? 68 ?
import asyncio
import base64
from uuid import uuid4

from .svg import make_svg

BUSY = {'searching', 'waiting_confirmation', 'generating_image', 'streaming_reply'}


async def run_agent(session, turn_id, text):
    tool = 'search'
    try:
        await asyncio.sleep(1.5)
        async with session.condition:
            session.emit('tool_finished', turn_id, {'tool': 'search', 'status': 'done', 'result': ['A fictional result about ' + text]})
            session.state = 'waiting_confirmation'
            session.confirmation_id = str(uuid4())
            session.confirmation = asyncio.get_running_loop().create_future()
            prompt = 'Illustration inspired by: ' + text
            session.emit('confirmation_required', turn_id, {'confirmationId': session.confirmation_id, 'prompt': prompt})
            confirmation = session.confirmation
        decision, final_prompt = await confirmation
        if decision == 'reject':
            async with session.condition:
                session.state = 'rejected'
                session.emit('turn_ended', turn_id, {'reason': 'rejected'})
            return
        async with session.condition:
            session.state = 'generating_image'
            tool = 'generate_image'
            fail = session.fail_next
            session.fail_next = False
            session.emit('tool_started', turn_id, {'tool': tool, 'status': 'in_progress'})
        await asyncio.sleep(4)
        async with session.condition:
            if fail:
                session.emit('tool_finished', turn_id, {'tool': tool, 'status': 'failed', 'error': 'Simulated image generation failure'})
                session.state = 'failed'
                session.emit('turn_ended', turn_id, {'reason': 'failed'})
                return
            svg = make_svg(final_prompt)
            url = 'data:image/svg+xml;base64,' + base64.b64encode(svg.encode()).decode()
            session.emit('tool_finished', turn_id, {'tool': tool, 'status': 'done', 'result': url})
            session.emit('image_generated', turn_id, {'imageUrl': url, 'prompt': final_prompt})
            session.state = 'streaming_reply'
            tool = None
        for character in 'Your image is ready. The illustration uses the approved prompt.':
            async with session.condition:
                session.emit('text_delta', turn_id, {'delta': character})
            await asyncio.sleep(0.08)
        async with session.condition:
            session.state = 'completed'
            session.emit('turn_ended', turn_id, {'reason': 'completed'})
    except asyncio.CancelledError:
        async with session.condition:
            if session.state in BUSY:
                if tool and session.state in {'searching', 'generating_image'}:
                    session.emit('tool_finished', turn_id, {'tool': tool, 'status': 'cancelled'})
                session.state = 'cancelled'
                session.emit('turn_ended', turn_id, {'reason': 'cancelled'})
        raise
    except Exception:
        async with session.condition:
            if session.state in BUSY:
                if tool:
                    session.emit('tool_finished', turn_id, {'tool': tool, 'status': 'failed', 'error': 'Agent execution failed'})
                session.state = 'failed'
                session.emit('turn_ended', turn_id, {'reason': 'failed'})
```

### ?????2026-11-21

- **????**?`backend/app/main.py`
- **?????**????? Agent????????????
- **?????**??????????????
- **?????**???????????????

#### 1. ???????????
```python
// ? 1 ? ~ ? 47 ?
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
```

#### 2. ???????????
```python
// ? 1 ? ~ ? 131 ?
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
```

