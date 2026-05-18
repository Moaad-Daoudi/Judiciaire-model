import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import Sidebar from '@/components/SideBar';
import InputArea from '@/components/InputArea';
import { FileText, Gavel, Search } from 'lucide-react';
import rtlDetect from 'rtl-detect';

interface Message {
  role: 'user' | 'ai';
  content: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [darkMode, setDarkMode] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Ref for auto-scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  // Dark mode effect
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const handleSendMessage = async (text: string) => {
    setIsLoading(true);
    setMessages(prev => [...prev, { role: 'user', content: text }]);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const data = await response.json();
      setMessages(prev => [...prev, { role: 'ai', content: data.reply }]);
    } catch (error) {
      console.error("Error connecting to backend:", error);
      setMessages(prev => [...prev, { role: 'ai', content: "Error: Could not connect to the legal AI backend." }]);
    } finally {
      setIsLoading(false);
    }
  };

  const quickStarts = [
    { icon: FileText, title: "Review Family Code", desc: "Analyze marriage and custody laws." },
    { icon: Gavel, title: "Nationality Rights", desc: "Understand citizenship requirements." },
    { icon: Search, title: "Kafala Procedures", desc: "Check guardianship regulations." },
  ];

  return (
    <div className="flex h-screen bg-slate-50 text-slate-800 dark:bg-[#0f172a] dark:text-slate-100 transition-colors duration-200">
      <Sidebar darkMode={darkMode} setDarkMode={setDarkMode} />

      <main className="flex-1 flex flex-col overflow-hidden">
        {messages.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center p-8">
            <h1 className="text-4xl font-bold mb-4">AtlasLegalAI</h1>
            <p className="text-slate-500 mb-12">Ask questions about Moroccan Law.</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl">
              {quickStarts.map((item, i) => (
                <div key={i} className="bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-slate-700 p-6 rounded-2xl transition hover:shadow-lg">
                  <item.icon className="text-blue-500 mb-4" size={32} />
                  <h3 className="font-semibold mb-2">{item.title}</h3>
                  <p className="text-sm text-slate-500">{item.desc}</p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex-1 p-8 overflow-y-auto space-y-6">
            {messages.map((msg, index) => {
              const isRtl = rtlDetect.isRtlLang(rtlDetect.getLangDir(msg.content) || (msg.content.match(/[\u0600-\u06FF]/) ? 'ar' : 'en'));
              return (
                <div key={index} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`p-4 rounded-xl max-w-[80%] shadow-sm ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-white dark:bg-[#1e293b] border border-slate-200 dark:border-slate-700'}`}
                    dir={isRtl ? 'rtl' : 'ltr'}
                  >
                    {/* Markdown rendering handles bolding and newlines */}
                    <ReactMarkdown>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                </div>
              );
            })}
            {isLoading && (
              <div className="flex justify-start animate-pulse text-slate-400">AI is searching the laws...</div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
        <InputArea onSend={handleSendMessage} />
      </main>
    </div>
  );
}

export default App;