import React from "react";

export default function SchoolUpdates() {
  return (
    <section className="w-full pb-32" style={{ paddingLeft: "160px", paddingRight: "160px", paddingTop: "120px" }}>
      <div className="max-w-[1200px] mx-auto flex flex-col md:flex-row gap-16">
        
        {/* Left Column */}
        <div className="md:w-1/3 flex flex-col items-start">
          <h2 className="text-[48px] md:text-[56px] leading-[1.1] font-bold tracking-tight text-black mb-6">
            Stay up to date
          </h2>
          <button className="px-6 py-2 border border-black rounded-full text-[15px] font-medium hover:bg-black hover:text-white transition-colors">
            View all
          </button>
        </div>

        {/* Right Column - Grid */}
        <div className="md:w-2/3 grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-12">
          
          {/* Card 1 */}
          <div className="flex flex-col group cursor-pointer">
            <div className="w-full h-[280px] bg-blue-200 flex flex-col items-center justify-center text-center p-8 mb-4">
              <h3 className="text-[32px] font-bold text-black leading-tight">
                GCSE<br/>RESULTS<br/>DAY<br/>2025
              </h3>
            </div>
            <p className="text-[15px] text-gray-800 leading-snug mb-3">
              74% of surveyed students improved their grades while using BoostAI.
            </p>
            <p className="text-[14px] text-black underline underline-offset-4 group-hover:text-gray-600 transition-colors">
              See our full GCSE 2025 results
            </p>
          </div>

          {/* Card 2 */}
          <div className="flex flex-col group cursor-pointer">
            <div className="w-full h-[280px] bg-blue-950 flex flex-col items-center justify-center text-center p-8 mb-4">
              <p className="text-blue-300 text-[13px] font-bold mb-4">New Feature</p>
              <h3 className="text-[28px] font-bold text-white leading-tight">
                Handwrite<br/>your equations
              </h3>
            </div>
            <p className="text-[15px] text-gray-800 leading-snug">
              No More Forgetting Your Answers
            </p>
          </div>

          {/* Card 3 */}
          <div className="flex flex-col group cursor-pointer">
            <div className="w-full h-[280px] bg-blue-950 flex flex-col items-center justify-center text-center p-8 mb-4">
              <p className="text-white text-[13px] font-bold mb-4">Update</p>
              <h3 className="text-[28px] font-bold text-white leading-tight">
                Cross-subject<br/>Learning
              </h3>
            </div>
            <p className="text-[15px] text-gray-800 leading-snug">
              Connect concepts across disciplines
            </p>
          </div>

          {/* Card 4 */}
          <div className="flex flex-col group cursor-pointer">
            <div className="w-full h-[280px] bg-blue-950 flex flex-col items-center justify-center text-center p-8 mb-4">
              <h3 className="text-[28px] font-bold text-white leading-tight">
                The First<br/>AI Tutor<br/>for GCSE,<br/>A-Level & IB
              </h3>
            </div>
            <p className="text-[15px] text-gray-800 leading-snug">
              How BoostAI began
            </p>
          </div>

        </div>

      </div>
    </section>
  );
}
