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
