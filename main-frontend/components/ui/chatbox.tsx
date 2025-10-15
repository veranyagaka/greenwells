'use client';
import React, { useEffect, useRef, useState } from 'react';
import { getSocket } from '../../lib/socket';
import { postChatMessage } from '@/lib/api';

type Msg = { id: number | string; sender: string; text: string; at?: string };

export default function ChatBox({ orderId, me = 'driver' }: { orderId?: number; me?: string }) {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [text, setText] = useState('');
  const feedRef = useRef<HTMLDivElement | null>(null);

  // If socket exists, use it; otherwise mock receiving echoes.
  useEffect(() => {
    const socket = getSocket();
    if (!socket) {
      // mock incoming pings
      const interval = setInterval(() => {
        setMessages(prev => [...prev, { id: Date.now(), sender: 'customer', text: 'Ping from customer — are you nearby?', at: new Date().toISOString() }]);
      }, 20000);
      return () => clearInterval(interval);
    } else {
      socket.on('message', (msg: Msg) => setMessages(prev => [...prev, msg]));
      return () => { socket.off('message'); }
    }
  }, []);

  useEffect(() => {
    feedRef.current?.lastElementChild?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  async function send() {
    if (!text.trim()) return;
    const payload = { orderId, sender: me, text: text.trim() };
    // optimistic update
    const optimistic = { id: 'temp-' + Date.now(), sender: me, text: text.trim(), at: new Date().toISOString() };
    setMessages(m => [...m, optimistic]);
    setText('');
    try {
      const res: { message?: Msg } = await postChatMessage(payload);
      // in mock mode res.message echoes back; replace temp id
      if (res?.message) {
        setMessages(m => m.map(x => (
          x.id === optimistic.id
            ? { id: res.message!.id, sender: res.message!.sender, text: res.message!.text, at: new Date().toISOString() }
            : x
        )));
      }
    } catch (err) {
      console.error('send failed', err);
    }
  }

  return (
    <div className="flex flex-col h-full shadow rounded bg-white">
      <div ref={feedRef} className="flex-1 overflow-auto p-3 space-y-2">
        {messages.map(m => (
          <div key={String(m.id)} className={`flex ${m.sender === me ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[80%] p-2 rounded ${m.sender === me ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
              <div className="text-sm">{m.text}</div>
              <div className="text-xs opacity-60 mt-1">{new Date(m.at || Date.now()).toLocaleTimeString()}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="p-3 border-t flex items-center gap-3">
        <input value={text} onChange={(e)=>setText(e.target.value)} onKeyDown={(e)=>{ if(e.key==='Enter') send(); }} placeholder="Type message..." className="flex-1 p-2 border rounded" />
        <button onClick={send} className="px-4 py-2 bg-blue-600 text-white rounded">Send</button>
      </div>
    </div>
  );
}
