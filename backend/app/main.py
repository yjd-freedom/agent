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
