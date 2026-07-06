import React from "react";

export default function UnivVideoPreview() {
  return (
    <section className="w-full pb-32" style={{ paddingLeft: "120px", paddingRight: "120px" }}>
      <div className="max-w-[1200px] mx-auto">
        
        {/* Main Card Container */}
        <div className="w-full rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.08)] overflow-hidden flex flex-col">
          
          {/* Top Update Bar */}
          <div className="px-8 py-4 border-b border-gray-100">
            <p className="text-[14px] font-medium text-blue-200 flex items-center gap-2">
              <span className="text-gray-300">✦</span> Jan 17 update: Added practice test creation from past papers
            </p>
          </div>

          {/* Content Area */}
          <div className="flex w-full h-[600px]">
            
            {/* Left Pink Area */}
            <div className="w-[75%] h-full bg-blue-300 p-8 relative flex flex-col items-center justify-center">
              
              {/* Lecture 2 Pill */}
              <div className="absolute top-8 left-8 bg-white px-4 py-2 rounded-xl shadow-sm flex items-center gap-2 cursor-pointer hover:bg-gray-50 transition-colors">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="black" xmlns="http://www.w3.org/2000/svg">
                  <path d="M4 12C4 8 8 4 12 4C16 4 20 8 20 12C20 16 16 20 12 20C8 20 4 16 4 12Z" stroke="black" strokeWidth="3" strokeDasharray="4 6" fill="none"/>
                </svg>
                <span className="text-[14px] font-bold text-black">Lecture 2</span>
                <svg className="w-4 h-4 ml-1 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
                </svg>
              </div>

              {/* Presentation Slide */}
              <div className="w-[85%] h-[80%] bg-white shadow-md p-8 flex flex-col relative group cursor-pointer">
                
                {/* Slide Header */}
                <div className="mb-6">
                  <p className="text-[14px] font-bold text-black leading-tight mb-2">BoostAI University<br/>London</p>
                  <h3 className="text-[40px] font-bold text-black tracking-tight">The Krebs Cycle</h3>
                </div>

                {/* Mock Diagram Area */}
                <div className="flex-grow border border-gray-200 bg-gray-50 bg-[url('https://images.unsplash.com/photo-1532094349884-543bc11b234d?q=80&w=800&auto=format&fit=crop&opacity=20')] bg-cover bg-center relative">
                   {/* Play Button Overlay */}
                   <div className="absolute inset-0 m-auto w-20 h-20 bg-white rounded-full shadow-xl flex items-center justify-center group-hover:scale-105 transition-transform">
                     <svg width="28" height="28" viewBox="0 0 24 24" fill="black"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                   </div>
                </div>

                {/* Slide Footer */}
                <div className="mt-6 flex justify-between items-center text-[13px] font-bold text-black">
                  <span>PJ 17 Jan 2026</span>
                  <span>BIOL101 - Biology 101</span>
                  <span>Lecture 2 Slide 6</span>
                </div>

              </div>
              
            </div>

            {/* Right Sidebar - AI Tutor */}
            <div className="w-full md:w-[30%] lg:w-[25%] h-full bg-white flex flex-col border-l border-gray-100">
              
              {/* Sidebar Header */}
              <div className="px-6 py-4 border-b border-gray-100 flex items-center gap-3 bg-gray-50/50">
                <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-600">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <span className="font-bold text-[15px] text-gray-800">BoostAI Tutor</span>
              </div>

              {/* Chat Messages */}
              <div className="flex-1 p-6 flex flex-col gap-6 overflow-y-auto">
                {/* User Message */}
                <div className="flex flex-col items-end">
                  <div className="bg-blue-500 text-white text-[13px] px-4 py-3 rounded-2xl rounded-tr-sm max-w-[90%] shadow-sm leading-relaxed">
                    Can you summarize the main products of this cycle?
                  </div>
                  <span className="text-[10px] text-gray-400 mt-2">10:42 AM</span>
                </div>

                {/* AI Message */}
                <div className="flex flex-col items-start">
                  <div className="bg-gray-100 text-gray-800 text-[13px] px-4 py-3 rounded-2xl rounded-tl-sm max-w-[95%] shadow-sm leading-relaxed">
                    <p className="mb-2">For each turn of the Krebs cycle (per Acetyl-CoA), the products are:</p>
                    <ul className="list-disc pl-4 space-y-1">
                      <li>3 NADH</li>
                      <li>1 FADH₂</li>
                      <li>1 ATP (or GTP)</li>
                      <li>2 CO₂</li>
                    </ul>
                  </div>
                  <span className="text-[10px] text-gray-400 mt-2">10:42 AM</span>
                </div>
              </div>

              {/* Input Area */}
              <div className="p-4 border-t border-gray-100 bg-gray-50/50">
                <div className="relative flex items-center">
                  <input 
                    type="text" 
                    placeholder="Ask about this slide..." 
                    className="w-full bg-white border border-gray-200 rounded-full px-4 py-3 text-[13px] focus:outline-none focus:border-blue-300 focus:ring-2 focus:ring-blue-100 shadow-sm"
                    disabled
                  />
                  <div className="absolute right-2 w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center cursor-pointer hover:bg-blue-600 transition-colors">
                    <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </div>
                </div>
              </div>

            </div>

          </div>

        </div>

      </div>
    </section>
  );
}
