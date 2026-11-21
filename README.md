# Streaming Agent Chat

A small simulated agent demonstrates a server-driven search, human confirmation, SVG generation, and character-by-character response. No LLM, search service, or image model is called.

## Requirements and setup

- Python 3.11+, Node.js and npm.
- From the project root, install the backend dependencies in your chosen Python environment: `python -m pip install -r backend/requirements.txt`.
- Install the frontend dependencies: `cd frontend && npm ci`, then return to the project root.
- Start both services with `python dev.py`. On the supplied Windows environment this can be `conda run -n agent_test python dev.py`.
- Open `http://127.0.0.1:5173` (or the URL printed by Vite). The backend listens on port 18000; the frontend proxies `/health` and `/api` to it. Stop the launcher with Ctrl+C. If a port is occupied, stop the corresponding old development process first.
- Alternatively run `python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 18000` and, in a second terminal, `cd frontend && npm run dev`.
- Run `cd frontend && npm run build` to type-check and build. `GET /health` returns `{"status":"ok"}`.

## Structure

`backend/app/main.py` provides HTTP and SSE endpoints; `store.py` holds sessions and event logs; `agent.py` runs the state machine; `svg.py` generates escaped SVG. `frontend/src/main.tsx` projects events into the chat and debug controls. `dev.py` launches the development servers. `CHANGES.md` records changes.

## Events and state

Each event has `seq`, `type`, `sessionId`, `turnId`, `timestamp`, and `data`. Sequence numbers increase within each session. SSE uses `id`, `event`, and JSON `data`.

| Event | Key data | Trigger |
| --- | --- | --- |
| `user_message` | `text` | Message accepted |
| `turn_started` | `message` | Turn created |
| `tool_started` | `tool`, `status` | Search or image generation starts |
| `tool_finished` | `tool`, `status`, `result?`, `error?` | Tool finishes, fails, or is cancelled |
| `confirmation_required` | `confirmationId`, `prompt` | Search completes |
| `confirmation_resolved` | `confirmationId`, `decision`, `finalPrompt` | A decision is accepted |
| `image_generated` | `imageUrl`, `prompt` | SVG is ready |
| `text_delta` | `delta` | Each response character |
| `turn_ended` | `reason` | Turn ends: completed, rejected, cancelled, or failed |

The normal state path is `idle → searching → waiting_confirmation → generating_image → streaming_reply → completed`. Rejection ends at `rejected`; generation failure ends at `failed`; cancellation from any active state ends at `cancelled`. A new turn can start after a terminal state.

The session lock protects state transitions and event appends. One session accepts only one active loop: messages sent while busy return HTTP 409, including during confirmation. A confirmation is accepted once. Cancellation stops the task and emits one terminal event. Image failure is injected once, is not retried, and ends the turn as failed. The browser may start another turn afterwards.

Execution runs independently of SSE connections. The server stores events in order and uses the same condition lock for appending and waiting, so replay and live delivery have no subscription gap. Reconnection requests events after the last sequence number; the client ignores already-seen sequences. On refresh the browser reuses its saved session ID and replays from zero. Sessions are **in memory**: restarting the backend loses them. This is different from a browser refresh or network disconnection. A process restart requires a new session.

## Seven demo scenarios

1. Enter a message, press **Send**, then **Approve**. Search completes, the confirmation card appears, the image is generated, and the reply streams until `completed`.
2. Send a message, edit the prompt in the card and choose **Edit and approve**. The SVG displays the edited text.
3. Approve a message and press **Cancel** while image generation is in progress. The turn ends `cancelled` without a successful image.
4. During the character-by-character reply, press **Disconnect**. After a few seconds the stream reconnects and the complete reply appears without duplicated characters.
5. Enable **Image generation fails**, send a message and approve it. The next generation fails, its tool status and error are visible, and the turn ends `failed` without retry.
6. During an active turn, press **Send again**. A 409 message is displayed and no second loop starts.
7. While a confirmation card is waiting, type another message and press **Send**. The request is rejected with a visible message; the original card remains available.

Also check **Reject**, repeated approval, cancellation in other active states, and refreshing while waiting for confirmation.

## AI use and limitations

Codex was used to implement and inspect this project; see `ai-logs/README.md` for the status of original session exports and usage records. The workflow and search results are scripted. The SVG is a placeholder, not an image-model result. This demo uses a single in-memory server process, so it is not a multi-worker or durable production service. No authentication is provided. UI verification of every scenario and the external submission are tracked separately; do not treat unperformed checks as passed.
