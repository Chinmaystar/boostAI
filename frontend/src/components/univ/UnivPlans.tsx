import React from "react";

export default function UnivPlans() {
  return (
    <section className="w-full pb-32" style={{ paddingTop: "80px" }}>
      <div className="max-w-[1100px] mx-auto px-6">
        
        {/* Header */}
        <div className="mb-20 text-center max-w-[800px] mx-auto">
          <h2 className="text-[48px] md:text-[56px] font-bold tracking-tight text-black mb-6 leading-[1.1]">Let's start excelling</h2>
          <p className="text-[20px] text-gray-700 leading-relaxed">
            All-in-one revision for just one subscription. <span className="font-bold text-black">Always free to start.</span>
          </p>
        </div>

        {/* Pricing Cards Container */}
        <div className="w-full flex flex-col md:flex-row items-center justify-center gap-8 lg:gap-12">
          
          {/* Monthly Plan */}
          <div className="w-full md:w-[45%] max-w-[480px] bg-white/90 backdrop-blur-sm rounded-[40px] p-10 lg:p-14 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_40px_rgb(0,0,0,0.08)] transition-all duration-300 border border-white flex flex-col">
            <h3 className="text-[32px] font-bold text-black mb-4">Monthly</h3>
            <p className="text-[16px] text-gray-500 mb-12">Monthly billing, full access, cancel anytime.</p>
            
            <div className="flex items-end gap-2 mb-12">
              <span className="text-[64px] font-bold text-black leading-none tracking-tight">£24.99</span>
              <span className="text-[16px] text-gray-500 mb-2 font-medium">/ mo</span>
            </div>

            <ul className="flex flex-col gap-4 mb-16 text-[15px] text-gray-700 font-medium">
              <li className="flex items-center gap-3">
                <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
                Unlimited AI explanations
              </li>
              <li className="flex items-center gap-3">
                <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
                Automatic document sorting
              </li>
              <li className="flex items-center gap-3">
                <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
                Custom flashcard generation
              </li>
            </ul>

            <div className="mt-auto">
              <button className="w-full py-4 bg-gray-100 hover:bg-gray-200 text-black font-bold rounded-full mb-4 transition-colors text-[16px]">
                Start for free
              </button>
              <p className="text-[13px] text-gray-500 text-center font-medium">No credit card required.</p>
            </div>
          </div>

          {/* Annual Plan */}
          <div className="w-full md:w-[50%] max-w-[500px] bg-[#0F172A] rounded-[40px] p-10 lg:p-14 shadow-[0_20px_50px_rgba(15,23,42,0.2)] hover:shadow-[0_30px_60px_rgba(15,23,42,0.3)] hover:-translate-y-2 transition-all duration-300 border border-slate-800 flex flex-col relative overflow-hidden">
            <div className="absolute top-6 right-6 bg-yellow-400 text-yellow-950 text-[13px] font-bold px-4 py-1.5 rounded-full shadow-sm">
              Launch offer - 50%
            </div>
            
            <h3 className="text-[32px] font-bold text-white mb-4">Annual</h3>
            <p className="text-[16px] text-slate-300 mb-12">Yearly billing, full access. Best value.</p>
            
            <div className="flex items-end gap-2 mb-2">
              <span className="text-[64px] font-bold text-white leading-none tracking-tight">£12.50</span>
              <span className="text-[16px] text-slate-300 mb-2 font-medium">/ mo</span>
            </div>
            <p className="text-[14px] text-slate-400 mb-10 font-medium">Billed as £150 every 12 months, cancel anytime.</p>

            <ul className="flex flex-col gap-4 mb-16 text-[15px] text-slate-50 font-medium">
              <li className="flex items-center gap-3">
                <svg className="w-5 h-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
                Unlimited AI explanations
              </li>
              <li className="flex items-center gap-3">
                <svg className="w-5 h-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
                Automatic document sorting
              </li>
              <li className="flex items-center gap-3">
                <svg className="w-5 h-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
                Custom flashcard generation
              </li>
              <li className="flex items-center gap-3">
                <svg className="w-5 h-5 text-yellow-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                </svg>
                Priority new features access
              </li>
            </ul>

            <div className="mt-auto">
              <button className="w-full py-4 bg-white hover:bg-gray-50 text-black font-bold rounded-full mb-4 transition-colors text-[16px] shadow-lg shadow-black/10">
                Start for free
              </button>
              <p className="text-[13px] text-slate-400 text-center font-medium">No credit card required.</p>
            </div>
            
            {/* Background Glow */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-slate-600 rounded-full blur-[100px] opacity-20 pointer-events-none"></div>
          </div>

        </div>

      </div>
    </section>
  );
}
