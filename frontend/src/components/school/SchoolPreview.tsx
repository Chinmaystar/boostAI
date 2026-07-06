import React from "react";

export default function SchoolPreview() {
  return (
    <section className="w-full flex flex-col items-center relative" style={{ paddingLeft: "160px", paddingRight: "160px", paddingBottom: "120px" }}>
      
      <link href="https://fonts.googleapis.com/css2?family=Caveat:wght@500;600;700&display=swap" rel="stylesheet" />

      {/* Update Label */}
      <div className="w-full max-w-[1080px] flex items-center justify-center mb-10 mt-8">
        <div className="bg-blue-50/50 backdrop-blur-sm border border-blue-100 rounded-full px-6 py-2 flex items-center gap-3 shadow-[0_4px_20px_rgba(59,130,246,0.1)] hover:shadow-[0_4px_25px_rgba(59,130,246,0.15)] transition-shadow">
          <span className="text-[#3B82F6] animate-pulse">✦</span>
          <span className="text-blue-600 text-[14px] font-bold tracking-wide">
            Apr 2 update: Medly Shuffle - Adaptive Practice That Finds Your Weak Spots
          </span>
        </div>
      </div>

      {/* Tablet Mockup Outer Bezel */}
      <div className="w-full max-w-[1080px] rounded-[36px] bg-gray-900 p-4 sm:p-6 shadow-[0_40px_100px_-20px_rgba(0,0,0,0.3)] relative group">
        
        {/* Tablet Inner Screen */}
        <div className="w-full h-full bg-[#f8f9fa] rounded-[24px] overflow-hidden relative flex flex-col min-h-[600px] border border-gray-800">
          
          {/* Mockup Header (App-like toolbar) */}
          <div className="flex items-center justify-between px-6 py-4 bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-10">
            {/* Left Pill */}
            <div className="bg-white border border-gray-200 rounded-[12px] px-4 py-2.5 flex items-center gap-3 shadow-sm hover:shadow-md transition-shadow cursor-pointer">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#64748b" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 12v.01M8 12v.01M12 12v.01M16 12v.01M20 12v.01" />
              </svg>
              <span className="text-[14px] font-bold text-gray-800">Forces and Matter</span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect>
                <line x1="9" y1="4" x2="9" y2="20"></line>
              </svg>
            </div>
            
            {/* Right Pill */}
            <div className="bg-[#3B82F6] hover:bg-blue-600 rounded-[12px] px-5 py-2.5 flex items-center gap-2 shadow-[0_4px_12px_rgba(59,130,246,0.3)] transition-all cursor-pointer">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path>
                <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path>
              </svg>
              <span className="text-[14px] font-bold text-white tracking-wide">Textbook</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="opacity-80 ml-1">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
          </div>

          {/* Mockup Paper Area (Exam Style) */}
          <div className="flex-1 bg-white p-12 md:p-16 relative">
            
            {/* Subtle Grid Background */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: "radial-gradient(#000 1px, transparent 1px)", backgroundSize: "24px 24px" }}></div>

            {/* Content Container */}
            <div className="relative z-10 max-w-[800px] mx-auto">
              
              {/* Question 03 */}
              <div className="mb-20">
                <div className="flex items-start gap-6 mb-8">
                  {/* Q Number Badge */}
                  <div className="flex border-2 border-gray-300 rounded-lg overflow-hidden shrink-0 shadow-sm bg-gray-50">
                    <span className="px-3 py-1.5 text-[15px] font-bold border-r-2 border-gray-300 text-gray-700">0</span>
                    <span className="px-3 py-1.5 text-[15px] font-bold text-gray-700">3</span>
                  </div>
                  
                  {/* Q Text */}
                  <div className="flex-1 pt-1">
                    <p className="text-[17px] leading-[1.7] text-gray-800 font-medium">
                      A student attaches a weight to a spring, causing it to stretch. Describe what is meant by the limit of proportionality of the spring.
                    </p>
                  </div>
                  
                  {/* Marks */}
                  <div className="shrink-0 text-[14px] font-bold text-gray-400 pt-1.5 bg-gray-50 px-3 py-1 rounded-md border border-gray-100">
                    [2 marks]
                  </div>
                </div>

                {/* Handwritten Answer Container */}
                <div className="pl-[76px] relative">
                  {/* Decorative guide lines for handwriting */}
                  <div className="absolute top-[32px] left-[76px] right-0 h-[1px] bg-blue-100"></div>
                  <div className="absolute top-[64px] left-[76px] right-0 h-[1px] bg-blue-100"></div>
                  
                  <p 
                    className="text-[28px] leading-[32px] text-blue-600 font-bold relative z-10 -rotate-1 transform origin-left" 
                    style={{ fontFamily: "'Caveat', cursive" }}
                  >
                    The point beyond which force and extension are no longer directly proportional. The spring becomes permanently deformed.
                  </p>
                  
                  {/* Annotation Mark */}
                  <div className="absolute -right-8 top-2 text-green-500 font-bold text-[24px] rotate-12" style={{ fontFamily: "'Caveat', cursive" }}>
                    2/2 ✓
                  </div>
                </div>
              </div>

              {/* Question 04 */}
              <div className="opacity-90 transition-opacity hover:opacity-100">
                <div className="flex items-start gap-6">
                  {/* Q Number Badge */}
                  <div className="flex border-2 border-gray-300 rounded-lg overflow-hidden shrink-0 shadow-sm bg-gray-50">
                    <span className="px-3 py-1.5 text-[15px] font-bold border-r-2 border-gray-300 text-gray-700">0</span>
                    <span className="px-3 py-1.5 text-[15px] font-bold text-gray-700">4</span>
                  </div>
                  
                  <div className="flex-1 pt-1">
                    <p className="text-[17px] leading-[1.7] text-gray-800 font-medium mb-10">
                      An engineer is designing a new seated rowing machine shown in Fig.17.1.<br/>
                      The resistance is provided by two identical springs.
                    </p>
                    
                    {/* Beautiful Illustration Placeholder */}
                    <div className="w-full max-w-[400px] h-[240px] border-2 border-dashed border-gray-300 bg-gray-50 rounded-xl flex flex-col items-center justify-center text-gray-400 ml-2 group cursor-pointer hover:bg-blue-50/50 hover:border-blue-300 transition-colors">
                      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="mb-4 text-gray-300 group-hover:text-blue-400 transition-colors">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                        <circle cx="8.5" cy="8.5" r="1.5"></circle>
                        <polyline points="21 15 16 10 5 21"></polyline>
                      </svg>
                      <span className="font-medium text-[14px] group-hover:text-blue-500 transition-colors">Rowing Machine Illustration</span>
                    </div>
                  </div>
                </div>
              </div>

            </div>
          </div>

          {/* iPad Home Indicator */}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 w-32 h-1.5 bg-gray-300 rounded-full z-20"></div>

        </div>
      </div>
    </section>
  );
}
