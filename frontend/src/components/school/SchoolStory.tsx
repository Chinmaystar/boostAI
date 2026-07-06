import React from "react";

export default function SchoolStory() {
  return (
    <section className="w-full pb-32" style={{ paddingTop: "120px" }}>
      <div className="max-w-[1080px] mx-auto px-6">
        
        {/* Header */}
        <div className="text-center mb-16">
          <h2 className="text-[48px] md:text-[56px] leading-[1.1] font-bold tracking-tight text-black">
            Why we started BoostAI
          </h2>
        </div>

        {/* Video Placeholder */}
        <div className="w-full max-w-[860px] mx-auto bg-gray-200 rounded-3xl h-[300px] sm:h-[400px] md:h-[480px] relative overflow-hidden bg-cover bg-center shadow-xl" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1522202176988-66273c2fd55f?q=80&w=1200&auto=format&fit=crop')" }}>
          
          {/* Overlay elements to mock the YouTube player UI from the screenshot */}
          <div className="absolute inset-0 bg-black/20 hover:bg-black/10 transition-colors cursor-pointer group flex items-center justify-center">
            
            {/* Top Left Branding */}
            <div className="absolute top-4 left-4 flex items-center gap-3">
              <div className="w-10 h-10 bg-black/80 rounded-full flex items-center justify-center text-white font-bold text-xl">
                B
              </div>
              <div className="text-white drop-shadow-md">
                <p className="font-bold text-[18px]">Who are BoostAI?</p>
                <p className="text-[14px]">BoostAI</p>
              </div>
            </div>

            {/* Play Button */}
            <div className="w-16 h-12 bg-blue-600 rounded-xl flex items-center justify-center group-hover:bg-blue-500 transition-colors shadow-lg">
               <svg width="24" height="24" viewBox="0 0 24 24" fill="white"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            </div>

            {/* Bottom Controls */}
            <div className="absolute bottom-4 left-4">
              <div className="w-10 h-10 bg-black/50 hover:bg-black/70 rounded-full flex items-center justify-center text-white backdrop-blur-sm">
                 <svg width="20" height="20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
              </div>
            </div>

            <div className="absolute bottom-4 right-4 flex items-center gap-2 bg-black/50 hover:bg-black/70 rounded-full px-4 py-2 text-white backdrop-blur-sm text-sm font-medium">
              Watch on <span className="font-bold">YouTube</span>
            </div>

          </div>
        </div>

      </div>
    </section>
  );
}
