import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type AgentEvent = { seq: number; type: string; turnId: string; data: Record<string, any> };
type Turn = { id: string; message: string; reply: string; status: string; search?: string; imageTool?: string; image?: string; prompt?: string; confirmationId?: string; resolved?: boolean; error?: string };
const names = ['user_message', 'turn_started', 'tool_started', 'tool_finished', 'confirmation_required', 'confirmation_resolved', 'image_generated', 'text_delta', 'turn_ended'];
const busy = ['searching', 'waiting_confirmation', 'generating_image', 'streaming_reply'];

async function request(path: string, body?: object) {
  const response = await fetch(path, body === undefined ? undefined : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
  const data = await response.json();
  if (!response.ok) throw new Error(response.status === 409 ? 'Current operation is still running or already resolved.' : String(data.detail || 'Request failed'));
  return data;
}

function applyEvent(turns: Turn[], event: AgentEvent): Turn[] {
  if (event.type === 'user_message') return [...turns, { id: event.turnId, message: event.data.text, reply: '', status: 'searching' }];
  return turns.map(turn => {
    if (turn.id !== event.turnId) return turn;
    const next = { ...turn }, d = event.data;
    if (event.type === 'tool_started') { if (d.tool === 'search') next.search = 'in progress'; else { next.imageTool = 'in progress'; next.status = 'generating_image'; } }
    if (event.type === 'tool_finished') { if (d.tool === 'search') next.search = d.status; else next.imageTool = d.status; if (d.error) next.error = d.error; }
    if (event.type === 'confirmation_required') { next.confirmationId = d.confirmationId; next.prompt = d.prompt; next.status = 'waiting_confirmation'; }
    if (event.type === 'confirmation_resolved') { next.resolved = true; if (d.finalPrompt) next.prompt = d.finalPrompt; }
    if (event.type === 'image_generated') { next.image = d.imageUrl; next.status = 'streaming_reply'; }
    if (event.type === 'text_delta') { next.reply += d.delta; next.status = 'streaming_reply'; }
    if (event.type === 'turn_ended') next.status = d.reason;
    return next;
  });
}

function App() {
  const [session, setSession] = useState('');
  const [health, setHealth] = useState('checking');
  const [connection, setConnection] = useState('connecting');
  const [turns, setTurns] = useState<Turn[]>([]);
  const [message, setMessage] = useState('');
  const [edited, setEdited] = useState('');
  const [error, setError] = useState('');
  const [failure, setFailure] = useState(false);
  const source = useRef<EventSource | null>(null);
  const lastSeq = useRef(0);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const connectRef = useRef<() => void>(() => {});

  useEffect(() => {
    let active = true;
    fetch('/health').then(r => r.ok ? r.json() : Promise.reject()).then(d => active && setHealth(d.status)).catch(() => active && setHealth('unavailable'));
    (async () => {
      let id = localStorage.getItem('agentSession');
      if (id) {
        const response = await fetch(`/api/sessions/${id}`);
        if (response.status === 404) id = null;
        else if (!response.ok) throw new Error('Cannot check the saved session');
      }
      if (!id) { const created = await request('/api/sessions', {}); id = created.sessionId; localStorage.setItem('agentSession', id!); }
      if (active) setSession(id!);
    })().catch(e => active && setError(String(e)));
    return () => { active = false; };
  }, []);

  useEffect(() => {
    if (!session) return;
    let alive = true;
    const connect = () => {
      if (!alive) return;
      setConnection('connecting');
      const current = new EventSource(`/api/sessions/${session}/events?after=${lastSeq.current}`);
      source.current = current;
      current.onopen = () => setConnection('connected');
      current.onerror = () => { current.close(); if (alive) { setConnection('disconnected; reconnecting'); timer.current = setTimeout(connect, 1500); } };
      names.forEach(name => current.addEventListener(name, raw => {
        const event = JSON.parse((raw as MessageEvent).data) as AgentEvent;
        if (event.seq <= lastSeq.current) return;
        lastSeq.current = event.seq;
        setTurns(previous => applyEvent(previous, event));
        if (event.type === 'confirmation_required') setEdited(event.data.prompt);
        if (event.type === 'tool_started' && event.data.tool === 'generate_image') setFailure(false);
      }));
    };
    connectRef.current = connect;
    connect();
    return () => { alive = false; source.current?.close(); if (timer.current) clearTimeout(timer.current); };
  }, [session]);

  const base = `/api/sessions/${session}`;
  const current = turns.at(-1);
  const action = async (path: string, body: object) => { try { setError(''); await request(base + path, body); return true; } catch (e) { setError((e as Error).message); return false; } };
  const send = async (text: string) => { if (text.trim() && await action('/messages', { text })) setMessage(''); };
  const decide = (turn: Turn, decision: string) => action(`/confirmations/${turn.confirmationId}`, { decision, prompt: edited });
  const disconnect = () => { source.current?.close(); if (timer.current) clearTimeout(timer.current); setConnection('disconnected; reconnecting'); timer.current = setTimeout(() => connectRef.current(), 3500); };
  return <main><h1>Streaming Agent Chat</h1><p>Backend: {health} · Connection: {connection} · Status: {current?.status || 'idle'}</p>
    {error && <p role="alert" className="error">{error}</p>}
    <section aria-label="Chat">{turns.map(turn => <article key={turn.id}>
      <p><strong>You:</strong> {turn.message}</p><p>Search: {turn.search || 'pending'} · Image: {turn.imageTool || 'pending'}</p>
      {turn.confirmationId && <div className="card"><strong>Image prompt</strong><p>{turn.prompt}</p>{!turn.resolved && turn.status === 'waiting_confirmation' && <><textarea aria-label="Edit prompt" value={edited} onChange={e => setEdited(e.target.value)} /><div><button onClick={() => decide(turn, 'approve')}>Approve</button><button onClick={() => decide(turn, 'edit_approve')}>Edit and approve</button><button onClick={() => decide(turn, 'reject')}>Reject</button></div></>}</div>}
      {turn.image && <img src={turn.image} alt={`Generated placeholder: ${turn.prompt}`} />}
      {turn.reply && <p><strong>Agent:</strong> {turn.reply}</p>}{turn.error && <p className="error">{turn.error}</p>}<p>Status: {turn.status}</p>
    </article>)}</section>
    <form onSubmit={e => { e.preventDefault(); void send(message); }}><textarea aria-label="Message" value={message} onChange={e => setMessage(e.target.value)} /><div><button type="submit" disabled={!session}>Send</button><button type="button" disabled={!current || !busy.includes(current.status)} onClick={() => action('/cancel', {})}>Cancel</button></div></form>
    <section className="card"><h2>Debug Panel</h2><button onClick={disconnect} disabled={!session}>Disconnect</button><label><input type="checkbox" checked={failure} onChange={async e => { const enabled = e.target.checked; if (await action('/debug/image-failure', { enabled })) setFailure(enabled); }} /> Image generation fails</label><button onClick={() => send('Debug: send again')} disabled={!session}>Send again</button></section>
  </main>;
}

createRoot(document.getElementById('root')!).render(<App />);
