import React from "react";

export default function UnivFeatures() {
  return (
    <section
      className="w-full py-32"
      style={{ paddingLeft: "120px", paddingRight: "120px" }}
    >
      <div className="max-w-[1200px] mx-auto">
        {/* Intro Text */}
        <div className="max-w-[800px] mb-24 text-center mx-auto">
          <h2 className="text-[48px] md:text-[56px] font-bold tracking-tight text-black mb-6 leading-[1.1]">
            BoostAI makes you excel at
            <br />
            coursework and exams
          </h2>
          <p className="text-[20px] text-gray-700 leading-relaxed mb-4">
            BoostAI handles the mundane tasks. From note-taking,
            file-organising, flashcard making, assignment planning, practice
            exam building and more.
          </p>
          <p className="text-[20px] text-gray-700 font-medium leading-relaxed">
            You can focus on actually learning.
          </p>
        </div>

        {/* Features Container */}
        <div className="flex flex-col gap-12">
          
          {/* Feature 1: Effortlessly organised (Text Left, Image Right) */}
          <div className="bg-white/90 backdrop-blur-sm rounded-[40px] p-12 lg:p-16 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_40px_rgb(0,0,0,0.06)] transition-all duration-300 border border-white flex flex-col lg:flex-row items-center gap-16">
            <div className="lg:w-1/2">
              <h3 className="text-[36px] font-bold tracking-tight text-black mb-6">
                Effortlessly organised
              </h3>
              <p className="text-[18px] text-gray-600 leading-relaxed max-w-[480px]">
                BoostAI knows your syllabus and your modules, sorting your uploads
                for you automatically into weeks and modules.
              </p>
            </div>
            <div className="lg:w-1/2 w-full relative h-[360px] flex items-center justify-end">
              <div className="absolute right-0 bottom-0 w-[80%] h-[100%] bg-blue-100 rounded-2xl z-0"></div>
              <div className="w-[90%] h-[90%] bg-white rounded-2xl shadow-lg z-10 border border-gray-100 p-8 flex flex-col mr-8 overflow-hidden relative">
                <h4 className="font-bold text-[18px] mb-6 text-black">Electronics</h4>
                <div className="flex gap-4 mb-6 border-b border-gray-100 pb-3">
                  <span className="text-blue-600 font-bold text-[13px] bg-blue-50 px-4 py-1.5 rounded-full">
                    Course Materials
                  </span>
                  <span className="text-gray-400 font-semibold text-[13px] py-1.5">
                    Assessments
                  </span>
                  <span className="text-gray-400 font-semibold text-[13px] py-1.5">
                    Glossary
                  </span>
                </div>
                <div className="flex items-start gap-4 mb-6 bg-gray-50 p-4 rounded-xl">
                  <div className="w-10 h-10 bg-blue-100 rounded-lg flex-shrink-0"></div>
                  <div>
                    <div className="font-bold text-[14px] text-gray-800">Module Guide</div>
                    <div className="text-[12px] text-gray-500 mt-1">
                      Guide 12/09/25
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-3 text-blue-500 font-bold text-[14px] mt-auto">
                  <div className="w-6 h-6 rounded-full bg-blue-100 flex items-center justify-center">
                    <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                  Week 1
                </div>
              </div>
            </div>
          </div>

          {/* Feature 2: Understand everything (Image Left, Text Right) */}
          <div className="bg-white/90 backdrop-blur-sm rounded-[40px] p-12 lg:p-16 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_40px_rgb(0,0,0,0.06)] transition-all duration-300 border border-white flex flex-col lg:flex-row-reverse items-center gap-16">
            <div className="lg:w-1/2 lg:pl-12">
              <h3 className="text-[36px] font-bold tracking-tight text-black mb-6">
                Understand everything
              </h3>
              <p className="text-[18px] text-gray-600 leading-relaxed max-w-[480px]">
                BoostAI breaks down complex topics, referencing previous lectures
                and readings so you can understand everything you need to learn
                for assignments.
              </p>
            </div>
            <div className="lg:w-1/2 w-full relative h-[360px] flex items-center justify-start">
              <div className="absolute left-0 bottom-0 w-[80%] h-[100%] bg-purple-100 rounded-2xl z-0"></div>
              <div className="w-[90%] h-full bg-white rounded-2xl shadow-lg z-10 border border-gray-100 p-8 flex flex-col ml-8 overflow-hidden relative">
                <div className="flex items-start gap-4 mb-6">
                  <div className="w-16 h-12 border border-purple-200 bg-purple-50 rounded-lg flex items-center justify-center text-[11px] font-bold text-purple-600 flex-shrink-0">
                    Slide
                  </div>
                  <div className="bg-gray-50 border border-gray-100 px-5 py-3 rounded-2xl rounded-tl-none text-[13px] text-gray-700 font-medium flex-grow shadow-sm">
                    Explain this diagram to me.
                  </div>
                </div>
                <div className="mt-4 text-[13px] leading-relaxed text-gray-600 bg-blue-50/50 p-5 rounded-2xl border border-blue-50">
                  <p className="font-bold text-blue-900 mb-2 flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                    BoostAI
                  </p>
                  <p className="mb-3">
                    This question asks about the Luebering-Rapoport pathway, an
                    alternative route in red blood cells where 1,3-BPG bypasses
                    the normal ATP-generating step.
                  </p>
                  <p>
                    In normal glycolysis, 1,3-BPG is converted to 3PG by
                    phosphoglycerate kinase, producing ATP.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Feature 3: Exam prep (Text Left, Image Right) */}
          <div className="bg-white/90 backdrop-blur-sm rounded-[40px] p-12 lg:p-16 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_40px_rgb(0,0,0,0.06)] transition-all duration-300 border border-white flex flex-col lg:flex-row items-center gap-16">
            <div className="lg:w-1/2">
              <h3 className="text-[36px] font-bold tracking-tight text-black mb-6">
                Exam prep
              </h3>
              <p className="text-[18px] text-gray-600 leading-relaxed max-w-[480px]">
                BoostAI helps you prepare for assignments by guiding you through
                your course materials, making you flashcards and practice tests to
                help you apply your understanding.
              </p>
            </div>
            <div className="lg:w-1/2 w-full relative h-[360px] flex items-center justify-end">
              <div className="absolute right-0 top-0 w-[90%] h-[100%] bg-pink-100 rounded-2xl z-0"></div>
              <div className="w-[90%] h-full bg-white rounded-2xl shadow-lg z-10 border border-gray-100 p-8 flex flex-col mr-8 overflow-hidden relative">
                <div className="flex gap-4 h-[55%] border-b border-gray-100 pb-5 mb-5">
                  <div className="w-1/3 h-full flex flex-col gap-3">
                    <div className="flex-1 bg-pink-200 rounded-lg shadow-sm opacity-50"></div>
                    <div className="flex-1 bg-pink-200 rounded-lg shadow-sm opacity-50"></div>
                    <div className="flex-1 bg-pink-200 rounded-lg shadow-sm opacity-50"></div>
                  </div>
                  <div className="w-2/3 h-full bg-pink-50 rounded-xl shadow-inner border border-pink-100 p-6 flex items-center justify-center text-center font-bold text-pink-900 text-[14px] leading-relaxed">
                    A measure of the responsiveness of the quantity demanded of a
                    good to a change in its price.
                  </div>
                </div>
                <div>
                  <h4 className="font-bold text-[14px] mb-3 text-gray-800 flex items-center gap-2">
                    <svg className="w-4 h-4 text-pink-500" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
                    </svg>
                    Flashcards (15)
                  </h4>
                  <div className="flex items-center justify-between text-[12px] text-gray-600 bg-gray-50 border border-gray-100 p-3 rounded-lg mb-2 shadow-sm">
                    <span className="font-bold text-gray-400 w-4">1</span>
                    <span className="font-bold w-[35%] text-gray-700">Market Eq.</span>
                    <span className="w-[55%] truncate">
                      The price and quantity level...
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[12px] text-gray-600 bg-gray-50 border border-gray-100 p-3 rounded-lg shadow-sm">
                    <span className="font-bold text-gray-400 w-4">2</span>
                    <span className="font-bold w-[35%] text-gray-700">Elasticity</span>
                    <span className="w-[55%] truncate">
                      A measure of the response...
                    </span>
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
