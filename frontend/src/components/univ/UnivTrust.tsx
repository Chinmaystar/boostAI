import React from "react";

export default function UnivTrust() {
  const logos = [
    { name: "UCL", font: "font-black tracking-tighter", size: "text-[32px]" },
    { name: "I M P E R I A L", font: "font-serif tracking-widest", size: "text-[24px]" },
    { name: "UNIVERSITY OF CAMBRIDGE", font: "font-serif", size: "text-[20px]" },
    { name: "Queen Mary", font: "font-serif italic", size: "text-[24px]" },
  ];

  return (
    <section className="w-full pb-24" style={{ paddingLeft: "120px", paddingRight: "120px" }}>
      <div className="max-w-[1200px] mx-auto flex flex-col items-start gap-8">
        
        <h3 className="text-[24px] font-bold text-black tracking-tight">
          Trusted by students from
        </h3>
        
        <div className="flex flex-wrap items-center gap-16 md:gap-24 opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
          
          {/* Mock Logos */}
          <div className="flex flex-col items-start">
            <span className="font-black text-[40px] tracking-tighter leading-none text-gray-800">UCL</span>
            <span className="text-[10px] text-gray-600 mt-1">University College London</span>
          </div>

          <div className="flex items-center">
            <span className="font-serif text-[28px] tracking-[0.2em] text-gray-700">IMPERIAL</span>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-8 h-10 border border-gray-400 bg-gray-100 flex items-center justify-center">
               <span className="text-[10px]">👑</span>
            </div>
            <div className="flex flex-col leading-none">
              <span className="font-serif text-[18px] text-gray-700">UNIVERSITY OF</span>
              <span className="font-serif text-[22px] text-gray-700">CAMBRIDGE</span>
            </div>
          </div>

          <div className="flex flex-col items-start leading-none">
            <span className="font-serif text-[28px] text-gray-700 italic">Queen Mary</span>
            <span className="text-[10px] text-gray-600 font-sans mt-1 ml-1">University of London</span>
          </div>

        </div>

      </div>
    </section>
  );
}
