import { Scale, MessageSquare, History, Wrench, Settings, HelpCircle, Sun, Moon } from 'lucide-react';

export default function Sidebar({ darkMode, setDarkMode }: { darkMode: boolean, setDarkMode: (val: boolean) => void }) {
  return (
    // 1. Sidebar Background: The Deep Navy color
    <aside className="w-64 bg-white dark:bg-[#0f172a] text-slate-800 dark:text-white p-6 flex flex-col h-screen border-r border-slate-200 dark:border-slate-700 transition-colors duration-200">
      
      {/* TOP SECTION: Logo & Navigation */}
      <div className="flex-1">
        
        {/* Logo Area */}
        <div className="flex flex-col items-center mb-8 gap-2">
          <Scale className="text-blue-600 dark:text-blue-500" size={40} />
          <h1 className="text-xl font-bold">Juridical AI</h1>
        </div>

        {/* Navigation */}
        <nav className="space-y-1">
          {/* Active Item */}
          <div className="bg-slate-100 dark:bg-[#1e293b] p-3 rounded-lg cursor-pointer flex items-center gap-3 font-medium">
            <MessageSquare size={18} /> New Chat
          </div>
          {/* Standard Items */}
          <div className="hover:bg-slate-50 dark:hover:bg-[#1e293b] p-3 rounded-lg cursor-pointer flex items-center gap-3 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white transition">
            <History size={18} /> History
          </div>
          <div className="hover:bg-slate-50 dark:hover:bg-[#1e293b] p-3 rounded-lg cursor-pointer flex items-center gap-3 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white transition">
            <Wrench size={18} /> Tools
          </div>
          <div className="hover:bg-slate-50 dark:hover:bg-[#1e293b] p-3 rounded-lg cursor-pointer flex items-center gap-3 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white transition">
            <Settings size={18} /> Settings
          </div>
          <div className="hover:bg-slate-50 dark:hover:bg-[#1e293b] p-3 rounded-lg cursor-pointer flex items-center gap-3 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white transition">
            <HelpCircle size={18} /> Help
          </div>
        </nav>
      </div>

      {/* Theme Toggle */}
      <div className="mb-4">
        <button 
          onClick={() => setDarkMode(!darkMode)}
          className="w-full flex items-center justify-center gap-2 p-2 rounded-lg bg-slate-100 dark:bg-[#1e293b] hover:bg-slate-200 dark:hover:bg-slate-700 transition"
        >
          {darkMode ? <Sun size={18} /> : <Moon size={18} />}
          <span>{darkMode ? "Light Mode" : "Dark Mode"}</span>
        </button>
      </div>

      {/* BOTTOM SECTION: Status (Dark Background style) */}
      {/* <div className="pt-4 space-y-2 text-sm">
        <div className="font-semibold text-slate-800 dark:text-white mb-2">System Status</div>
        <div className="border border-green-200 dark:border-green-900 bg-green-50 dark:bg-transparent rounded-lg p-3 space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <p className="text-green-700 dark:text-slate-300">Model: <span className="font-medium text-green-800 dark:text-white">Qwen 2.5 Online</span></p>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <p className="text-green-700 dark:text-slate-300">Vector DB: <span className="font-medium text-green-800 dark:text-white">Connected</span></p>
          </div>
        </div>
      </div> */}
      
    </aside>
  );
}