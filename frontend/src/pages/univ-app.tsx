import {
  Home,
  Clock,
  Hash,
  Download,
  Search,
  ZoomIn,
  Undo2,
  Redo2,
  Settings,
  Plus,
  Paperclip,
  ArrowUp,
  ChevronDown,
  Type,
  Bold,
  Italic,
  Underline,
  Pen
} from 'lucide-react';
import logo from '../assets/logo.avif';

export default function UnivAppPage() {
  return (
    <div className="flex h-screen bg-[#F3F8FB] overflow-hidden font-sans">
      {/* Left Pane - Editor */}
      <div className="flex-1 flex flex-col p-4 overflow-hidden relative border-r border-gray-200">
        
        {/* Editor Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {/* App Logo Placeholder */}
            <div className="w-8 h-8 rounded-lg flex items-center justify-center overflow-hidden">
              <img src={logo} alt="BoostAI Logo" className="w-full h-full object-cover" />
            </div>
            
            <button className="p-1.5 hover:bg-gray-100 rounded-md transition-colors text-gray-600">
              <Home size={18} />
            </button>
            
            <h1 className="font-medium text-gray-800 flex items-center gap-2">
              Summarize your lecture: Catching Up o...
              <div className="w-5 h-5 bg-white border border-gray-200 rounded flex items-center justify-center">
                <span className="w-3 h-3 border border-gray-400 rounded-sm"></span>
              </div>
            </h1>
          </div>
          
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-1 px-2 py-1 bg-white border border-gray-200 rounded-md text-xs font-medium text-gray-700">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span>
              Saved
            </div>
            <button className="p-1.5 hover:bg-gray-100 rounded-md transition-colors text-gray-600 border border-gray-200 bg-white ml-2">
              <Clock size={16} />
            </button>
            <button className="p-1.5 hover:bg-gray-100 rounded-md transition-colors text-gray-600 border border-gray-200 bg-white">
              <Hash size={16} />
            </button>
            <button className="flex items-center gap-1.5 px-3 py-1.5 bg-white border border-gray-200 rounded-md text-sm font-medium hover:bg-gray-50 transition-colors ml-2">
              <Download size={16} />
              Export
            </button>
          </div>
        </div>

        {/* Editor Canvas */}
        <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 overflow-y-auto mb-16 relative">
          {/* Main text area would go here */}
          <div className="p-12 w-full h-full cursor-text" />
        </div>

        {/* Floating Toolbar */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 bg-white rounded-full shadow-lg border border-gray-200 px-4 py-2 flex items-center gap-3">
          <button className="flex items-center gap-1 text-sm font-medium px-2 py-1 hover:bg-gray-50 rounded-md">
            Text <ChevronDown size={14} />
          </button>
          <div className="w-px h-5 bg-gray-200"></div>
          <button className="p-1.5 hover:bg-gray-100 rounded-md text-gray-700"><Bold size={16} /></button>
          <button className="p-1.5 hover:bg-gray-100 rounded-md text-gray-700"><Italic size={16} /></button>
          <button className="p-1.5 hover:bg-gray-100 rounded-md text-gray-700"><Underline size={16} /></button>
          <button className="p-1.5 hover:bg-gray-100 rounded-md text-gray-700"><Pen size={16} /></button>
          <div className="w-px h-5 bg-gray-200"></div>
          <button className="p-1.5 hover:bg-gray-100 rounded-md text-gray-700 flex items-center gap-1">
            <Plus size={16} /> <ChevronDown size={12} />
          </button>
          <div className="w-px h-5 bg-gray-200"></div>
          <button className="p-1.5 hover:bg-gray-100 rounded-md text-gray-700"><Search size={16} /></button>
          <button className="p-1.5 hover:bg-gray-100 rounded-md text-gray-700"><ZoomIn size={16} /></button>
          <div className="w-px h-5 bg-gray-200"></div>
          <button className="p-1.5 hover:bg-gray-100 rounded-md text-gray-700"><Undo2 size={16} /></button>
          <button className="p-1.5 hover:bg-gray-100 rounded-md text-gray-700"><Redo2 size={16} /></button>
          <div className="w-px h-5 bg-gray-200"></div>
          <button className="p-1.5 hover:bg-gray-100 rounded-md text-gray-700"><Settings size={16} /></button>
        </div>
      </div>

      {/* Right Pane - Chat */}
      <div className="w-[450px] bg-white flex flex-col overflow-hidden">
        
        {/* Chat Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center font-semibold text-sm">
              L
            </div>
            <h2 className="font-medium text-sm text-gray-800">Lecture Summary Request for Unknown Topic</h2>
          </div>
          <button className="p-1.5 hover:bg-gray-100 rounded-md text-gray-500">
            <Plus size={18} />
          </button>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
          <div className="flex flex-col gap-4">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded flex items-center justify-center overflow-hidden">
                <img src={logo} alt="BoostAI" className="w-full h-full object-cover" />
              </div>
              <span className="font-semibold text-gray-900 text-sm">BoostAI</span>
            </div>
            
            <div className="text-[15px] text-gray-800 leading-relaxed">
              Hey Asu. You mentioned you're catching up on lectures and want a summary, key terms, and a map of themes. I'll start with the first section of your summary doc so you can see how it looks.
            </div>
            
            <div className="text-[15px] text-gray-800 leading-relaxed">
              Let me first save a few things to remember you, and check what's in your workspace.
            </div>

            <div className="flex items-center gap-2 text-sm text-gray-500 cursor-pointer hover:text-gray-700">
              <span>Worked for 5 seconds</span>
              <ChevronDown size={14} />
            </div>

            <div className="text-[15px] text-gray-800 leading-relaxed">
              Since you haven't uploaded any lecture slides or notes yet, I can't pull from your course material to write the summary. What's the lecture topic you need to catch up on? Let me know and I'll find relevant material to work with.
            </div>
          </div>
        </div>

        {/* Chat Input */}
        <div className="p-4 bg-white border-t border-gray-100 mt-auto">
          {/* Quick Actions (optional, shown in some UIs but maybe not explicitly needed here, wait, mock shows a chip above input) */}
          <div className="mb-3 px-3 py-2 bg-blue-50 text-blue-700 rounded-lg text-sm font-medium w-fit flex items-center gap-2">
             <div className="w-4 h-4 bg-blue-500 rounded text-white flex items-center justify-center text-[10px] font-bold">S</div>
             Summarize your lecture: Catching Up on C...
          </div>

          <div className="bg-gray-50 rounded-2xl border border-gray-200 p-3 focus-within:ring-2 focus-within:ring-blue-100 transition-shadow">
            <textarea 
              placeholder="Ask anything"
              className="w-full bg-transparent resize-none outline-none text-[15px] text-gray-800 min-h-[40px] placeholder:text-gray-400"
              rows={1}
            />
            <div className="flex items-center justify-between mt-2">
              <div className="flex items-center gap-3">
                <button className="flex items-center gap-1.5 text-sm text-gray-500 hover:text-gray-700 font-medium">
                  <Plus size={16} /> Add docs
                </button>
                <button className="text-gray-400 hover:text-gray-600">
                  <Settings size={16} />
                </button>
              </div>
              <button className="w-8 h-8 bg-gray-200 text-gray-500 rounded-full flex items-center justify-center hover:bg-gray-300 transition-colors">
                <ArrowUp size={16} />
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
