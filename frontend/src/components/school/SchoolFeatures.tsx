import React from "react";

export default function SchoolFeatures() {
  return (
    <section
      className="w-full pb-32"
      style={{
        paddingLeft: "160px",
        paddingRight: "160px",
        paddingTop: "80px",
      }}
    >
      <div className="max-w-[1200px] mx-auto">
        <h2 className="text-[48px] leading-[1.1] font-bold tracking-[-0.02em] text-black max-w-[700px] mb-16">
          Everything you need for learning, personalised to your curriculum
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-x-8 gap-y-12">
          {/* Feature 1 */}
          <div className="bg-white/90 backdrop-blur-sm rounded-[32px] p-8 xl:p-10 shadow-[0_8px_30px_rgb(0,0,0,0.04)] flex flex-col items-center text-center hover:shadow-[0_20px_40px_rgb(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-300 border border-white">
            {/* Graphic */}
            <div className="w-full aspect-[4/3] bg-transparent rounded-xl mb-8 relative overflow-hidden flex justify-center items-end pb-8">
              {/* Decorative elements for Graphic 1 */}
              <div className="absolute left-[5%] bottom-8 w-[25%] h-[60%] bg-[#7DB9F8] rounded-t-lg opacity-60"></div>
              <div className="absolute right-[5%] bottom-8 w-[25%] h-[60%] bg-[#7DB9F8] rounded-t-lg opacity-60"></div>
              <div className="relative z-10 w-[45%] h-[75%] bg-[#2F93F6] rounded-t-lg flex flex-col items-center pt-4 px-3 shadow-md">
                <div className="w-full h-2 bg-white/30 rounded-full mb-2"></div>
                <div className="w-3/4 h-2 bg-white/30 rounded-full mb-6"></div>
                <div className="w-full h-1/2 bg-[#E1F0FF] rounded-sm mt-auto relative">
                  <svg
                    className="absolute inset-0 w-full h-full text-[#2F93F6] p-1"
                    viewBox="0 0 100 50"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="4"
                  >
                    <polyline points="10,40 30,20 50,30 70,10 90,25" />
                    <circle cx="10" cy="40" r="4" fill="currentColor" />
                    <circle cx="30" cy="20" r="4" fill="currentColor" />
                    <circle cx="50" cy="30" r="4" fill="currentColor" />
                    <circle cx="70" cy="10" r="4" fill="currentColor" />
                    <circle cx="90" cy="25" r="4" fill="currentColor" />
                  </svg>
                </div>
              </div>
            </div>
            <h3 className="text-[22px] font-bold text-black mb-3">
              Textbooks with a tutor
            </h3>
            <p className="text-[15px] leading-[24px] text-blue-400 max-w-[280px]">
              Written in a way you understand, with BoostAI by your side to help
              you figure out concepts.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="bg-white/90 backdrop-blur-sm rounded-[32px] p-8 xl:p-10 shadow-[0_8px_30px_rgb(0,0,0,0.04)] flex flex-col items-center text-center hover:shadow-[0_20px_40px_rgb(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-300 border border-white">
            {/* Graphic */}
            <div className="w-full aspect-[4/3] bg-transparent rounded-xl mb-8 flex flex-col items-center justify-center pt-4">
              {/* Decorative elements for Graphic 2 */}
              <div className="w-[80%] mb-6">
                <div className="flex items-start gap-3 mb-2">
                  <span className="text-[#2F93F6] font-bold text-lg leading-none">
                    1
                  </span>
                  <div className="flex-1 pt-1">
                    <div className="w-full h-1.5 bg-[#2F93F6] rounded-full mb-2"></div>
                    <div className="w-3/4 h-1.5 bg-[#7DB9F8] rounded-full"></div>
                  </div>
                </div>
                <div className="pl-6 space-y-2 mt-3">
                  <div className="w-full h-1.5 bg-[#C6E2FF] rounded-full"></div>
                  <div className="w-5/6 h-1.5 bg-[#C6E2FF] rounded-full"></div>
                  <div className="w-4/5 h-1.5 bg-[#C6E2FF] rounded-full"></div>
                </div>
              </div>
              <div className="w-[80%]">
                <div className="flex items-start gap-3 mb-2">
                  <span className="text-[#2F93F6] font-bold text-lg leading-none">
                    2
                  </span>
                  <div className="flex-1 pt-1">
                    <div className="w-full h-1.5 bg-[#2F93F6] rounded-full mb-2"></div>
                    <div className="w-2/3 h-1.5 bg-[#7DB9F8] rounded-full"></div>
                  </div>
                </div>
                <div className="pl-6 mt-3 flex flex-col gap-2">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full border-2 border-[#2F93F6]"></div>
                    <div className="w-3/4 h-1.5 bg-[#C6E2FF] rounded-full"></div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full border-2 border-[#2F93F6]"></div>
                    <div className="w-2/3 h-1.5 bg-[#C6E2FF] rounded-full"></div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-[#2F93F6]"></div>
                    <div className="w-4/5 h-1.5 bg-[#C6E2FF] rounded-full"></div>
                  </div>
                </div>
              </div>
            </div>
            <h3 className="text-[22px] font-bold text-black mb-3">
              Exam-style questions
            </h3>
            <p className="text-[15px] leading-[24px] text-blue-400 max-w-[280px]">
              Questions built like the real thing. Near endless practice to get
              you ready.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="bg-white/90 backdrop-blur-sm rounded-[32px] p-8 xl:p-10 shadow-[0_8px_30px_rgb(0,0,0,0.04)] flex flex-col items-center text-center hover:shadow-[0_20px_40px_rgb(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-300 border border-white">
            {/* Graphic */}
            <div className="w-full aspect-[4/3] bg-transparent rounded-xl mb-8 relative overflow-hidden flex flex-col justify-center">
              {/* Decorative elements for Graphic 3 */}
              <div className="w-[80%] mx-auto mt-2 opacity-40 grayscale">
                <div className="flex items-start gap-3 mb-2">
                  <span className="text-[#2F93F6] font-bold text-lg leading-none">
                    1
                  </span>
                  <div className="flex-1 pt-1">
                    <div className="w-full h-1.5 bg-[#2F93F6] rounded-full mb-2"></div>
                    <div className="w-3/4 h-1.5 bg-[#7DB9F8] rounded-full"></div>
                  </div>
                </div>
                <div className="pl-6 space-y-2 mt-3">
                  <div className="w-full h-1.5 bg-[#C6E2FF] rounded-full"></div>
                  <div className="w-5/6 h-1.5 bg-[#C6E2FF] rounded-full"></div>
                </div>
              </div>

              <div className="absolute bottom-4 left-4 right-4 h-[60%] bg-[#B5DAFC] rounded-2xl p-6 flex flex-col gap-5 justify-center shadow-sm">
                <div className="flex items-center gap-4">
                  <div className="w-7 h-7 rounded-full bg-[#2F93F6] flex items-center justify-center text-white shrink-0">
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <polyline points="20 6 9 17 4 12"></polyline>
                    </svg>
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="w-full h-2 bg-[#7DB9F8] rounded-full"></div>
                    <div className="w-[85%] h-2 bg-[#7DB9F8] rounded-full opacity-70"></div>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-7 h-7 rounded-full bg-[#90C8FC] flex items-center justify-center text-white shrink-0">
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="3"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <line x1="18" y1="6" x2="6" y2="18"></line>
                      <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="w-[90%] h-2 bg-[#7DB9F8] rounded-full opacity-60"></div>
                    <div className="w-[60%] h-2 bg-[#7DB9F8] rounded-full opacity-60"></div>
                  </div>
                </div>
              </div>
            </div>
            <h3 className="text-[22px] font-bold text-black mb-3">
              Instant marking
            </h3>
            <p className="text-[15px] leading-[24px] text-blue-400 max-w-[280px]">
              Learn exam technique by doing. Attempt questions and get instant
              feedback to improve.
            </p>
          </div>

          {/* Feature 4 */}
          <div className="bg-white/90 backdrop-blur-sm rounded-[32px] p-8 xl:p-10 shadow-[0_8px_30px_rgb(0,0,0,0.04)] flex flex-col items-center text-center hover:shadow-[0_20px_40px_rgb(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-300 border border-white">
            {/* Graphic */}
            <div className="w-full aspect-[4/3] bg-transparent rounded-xl mb-8 flex items-center justify-center p-8">
              <div className="w-[80%] h-[80%] flex items-end justify-center gap-6 border-b-2 border-gray-200 pb-2">
                <div className="w-10 h-[40%] bg-[#B5DAFC] rounded-t-sm"></div>
                <div className="w-10 h-[60%] bg-[#7DB9F8] rounded-t-sm"></div>
                <div className="w-10 h-[30%] bg-[#B5DAFC] rounded-t-sm"></div>
                <div className="w-10 h-[85%] bg-[#2F93F6] rounded-t-sm"></div>
              </div>
            </div>
            <h3 className="text-[22px] font-bold text-black mb-3">
              Track your progress
            </h3>
            <p className="text-[15px] leading-[24px] text-blue-400 max-w-[280px]">
              See how you're improving over time with detailed analytics and
              performance insights.
            </p>
          </div>

          {/* Feature 5 */}
          <div className="bg-white/90 backdrop-blur-sm rounded-[32px] p-8 xl:p-10 shadow-[0_8px_30px_rgb(0,0,0,0.04)] flex flex-col items-center text-center hover:shadow-[0_20px_40px_rgb(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-300 border border-white">
            {/* Graphic */}
            <div className="w-full aspect-[4/3] bg-transparent rounded-xl mb-8 relative flex items-center justify-center">
              <div className="absolute w-[60%] aspect-square bg-[#7DB9F8] rounded-[24px] rotate-[-12deg] opacity-50 shadow-sm"></div>
              <div className="relative w-[60%] aspect-square bg-white border-[3px] border-[#2F93F6] rounded-[24px] shadow-lg p-6 flex flex-col items-center justify-center gap-5">
                <div className="w-[70%] h-2.5 bg-[#C6E2FF] rounded-full"></div>
                <div className="w-[90%] h-2.5 bg-[#C6E2FF] rounded-full"></div>
                <div className="w-[80%] h-2.5 bg-[#C6E2FF] rounded-full"></div>
              </div>
            </div>
            <h3 className="text-[22px] font-bold text-black mb-3">
              Interactive flashcards
            </h3>
            <p className="text-[15px] leading-[24px] text-blue-400 max-w-[280px]">
              Memorise key concepts faster with smart, spaced-repetition
              flashcards.
            </p>
          </div>

          {/* Feature 6 */}
          <div className="bg-white/90 backdrop-blur-sm rounded-[32px] p-8 xl:p-10 shadow-[0_8px_30px_rgb(0,0,0,0.04)] flex flex-col items-center text-center hover:shadow-[0_20px_40px_rgb(0,0,0,0.06)] hover:-translate-y-1 transition-all duration-300 border border-white">
            {/* Graphic */}
            <div className="w-full aspect-[4/3] bg-transparent rounded-xl mb-8 flex items-center justify-center">
              <div className="w-32 h-32 rounded-full border-[8px] border-[#B5DAFC] flex items-center justify-center opacity-80">
                <div className="w-20 h-20 rounded-full border-[8px] border-[#7DB9F8] flex items-center justify-center">
                  <div className="w-10 h-10 rounded-full bg-[#2F93F6]"></div>
                </div>
              </div>
            </div>
            <h3 className="text-[22px] font-bold text-black mb-3">
              Hit your targets
            </h3>
            <p className="text-[15px] leading-[24px] text-blue-400 max-w-[280px]">
              Set your target grades and let our AI guide you there step by
              step.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
