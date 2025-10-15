'use client';
import React, { useState } from 'react';

export default function VoiceAssistant({ onTranscribed }: { onTranscribed?: (text: string) => void }) {
  const [listening, setListening] = useState(false);
  const [supported] = useState(typeof window !== 'undefined' && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window));

  function getRecognition(): any {
    const win: any = window as any;
    const Rec = win.webkitSpeechRecognition || win.SpeechRecognition;
    if (!Rec) return null;
    const r = new Rec();
    r.lang = 'en-US';
    r.interimResults = false;
    r.maxAlternatives = 1;
    return r;
  }

  function start() {
    const rec = getRecognition();
    if (!rec) return alert('SpeechRecognition not supported in this browser');
    rec.onresult = (ev: any) => {
      const text = ev.results[0][0].transcript;
      onTranscribed?.(text);
    };
    rec.onend = () => setListening(false);
    rec.onerror = (e:any) => { console.error('rec error', e); setListening(false); };
    rec.start();
    setListening(true);
  }

  return (
    <div className="flex items-center gap-2">
      <button onClick={start} disabled={!supported} className={`px-3 py-2 rounded ${listening ? 'bg-red-500 text-white' : 'bg-blue-600 text-white'}`}>
        {listening ? 'Listening...' : 'Voice'}
      </button>
    </div>
  );
}
