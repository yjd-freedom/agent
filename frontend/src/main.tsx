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
