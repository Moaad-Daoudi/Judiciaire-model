import { SendHorizontal, Square } from 'lucide-react';
import { useState } from 'react';

export default function InputArea({ onSend, isLoading }: { onSend: (text: string) => void, isLoading?: boolean }) {
  const [text, setText] = useState("");

  const handleSent = () => {
    if (text.trim() && !isLoading) {
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
          disabled={isLoading}
        />
        {isLoading ? (
          <button
            disabled
            className="flex items-center justify-center w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-700 text-slate-800 dark:text-slate-200 transition-colors"
          >
            <Square fill="currentColor" size={16} />
          </button>
        ) : (
          <button
            onClick={handleSent}
            className="flex items-center justify-center w-10 h-10 rounded-full text-blue-500 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-500/10 dark:text-white dark:hover:text-blue-400 transition-colors cursor-pointer"
          >
            <SendHorizontal size={24} />
          </button>
        )}
      </div>
    </div>
  );
}