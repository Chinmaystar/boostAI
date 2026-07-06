import React from "react";

export default function UnivHero() {
  return (
    <section className="w-full pt-24 pb-32" style={{ paddingLeft: "120px", paddingRight: "120px" }}>
      <div className="max-w-[1200px] mx-auto flex flex-col items-start">
        
        <h1 className="text-[64px] md:text-[80px] font-bold leading-[1.05] tracking-tight text-black mb-6 max-w-[900px]">
          The all-in-one AI study partner for your course
        </h1>
        
        <p className="text-[20px] text-gray-700 leading-relaxed mb-10 max-w-[650px]">
          BoostAI helps you stay on top of your lectures, understand your course content and prepare for coursework and exams.
        </p>
        
        <div className="flex items-center gap-4">
          <a 
            href="/select" 
            className="px-8 py-3 bg-blue-700 rounded-full font-medium text-[16px] hover:bg-black transition-colors shadow-md"
            style={{ color: "white" }}
          >
            Sign up for Free
          </a>
          <a 
            href="/select" 
            className="px-8 py-3 bg-white border border-gray-300 rounded-full font-medium text-[16px] hover:bg-gray-50 transition-colors shadow-sm"
            style={{ color: "black" }}
          >
            Login
          </a>
        </div>

      </div>
    </section>
  );
}
