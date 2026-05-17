import { SendHorizontal } from 'lucide-react';
import { useState } from 'react';

export default function InputArea({ onSend } : { onSend: (text: string) => void}) {
  const [text, setText] = useState("");

  const handleSent = () => {
    if(text.trim()) {
      onSend(text);
      setText("");
    }
  }

  return (
    <div className="p-6">
      <div className="max-w-2xl mx-auto relative flex items-center bg-white dark:bg-white/10 backdrop-blur-md border border-slate-200 dark:border-white/20 rounded-full px-6 py-4 shadow-xl">
        <input 
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSent()}
          className="flex-1 bg-transparent outline-none text-slate-800 dark:text-white placeholder-slate-400 dark:placeholder-slate-300"
          placeholder="Ask a legal question..." 
        />
        <button 
          onClick={handleSent}
          className="text-blue-500 hover:text-blue-600 dark:text-white dark:hover:text-blue-400 transition-colors cursor-pointer"
        >
          <SendHorizontal size={24} />
        </button>
      </div>
    </div>
  );
}