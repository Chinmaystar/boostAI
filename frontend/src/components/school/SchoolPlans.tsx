import React from "react";

export default function SchoolPlans() {
  return (
    <section className="w-full pb-32" style={{ paddingLeft: "160px", paddingRight: "160px", paddingTop: "120px" }}>
      <div className="max-w-[1200px] mx-auto px-6">
        
        {/* Header */}
        <div className="mb-20 text-center max-w-[800px] mx-auto">
          <h2 className="text-[48px] md:text-[56px] leading-[1.1] font-bold tracking-tight text-black mb-6">
            Let's start excelling
          </h2>
          <p className="text-[20px] text-gray-700 leading-relaxed">
            All-in-one revision for just one subscription. <span className="font-bold text-black">Always free to start.</span>
          </p>
        </div>

        {/* Pricing Cards Container */}
        <div className="w-full flex flex-col md:flex-row items-stretch justify-center gap-8 lg:gap-12 mb-12">
          
          {/* Monthly Plan */}
          <div className="w-full md:w-[45%] max-w-[480px] bg-white/90 backdrop-blur-sm rounded-[40px] p-10 lg:p-14 shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_40px_rgb(0,0,0,0.08)] transition-all duration-300 border border-white flex flex-col">
            <h3 className="text-[32px] font-bold text-black mb-4">Monthly</h3>
            <p className="text-[16px] text-gray-500 mb-12">Monthly billing, full access, cancel anytime.</p>
            
            <div className="flex items-end gap-2 mb-12">
              <span className="text-[64px] font-bold text-black leading-none tracking-tight">£24.99</span>
              <span className="text-[16px] text-gray-500 mb-2 font-medium">/ mo</span>
            </div>

            <div className="mt-auto">
              <button className="w-full py-4 bg-gray-100 hover:bg-gray-200 text-black font-bold rounded-full mb-4 transition-colors text-[16px]">
                Start for Free
              </button>
              <p className="text-[13px] text-gray-500 text-center font-medium">Always free to start. No credit card required.</p>
            </div>
          </div>

          {/* Annual Plan */}
          <div className="w-full md:w-[50%] max-w-[500px] bg-[#0F172A] rounded-[40px] p-10 lg:p-14 shadow-[0_20px_50px_rgba(15,23,42,0.2)] hover:shadow-[0_30px_60px_rgba(15,23,42,0.3)] hover:-translate-y-2 transition-all duration-300 border border-slate-800 flex flex-col relative overflow-hidden">
            <div className="absolute top-6 right-6 bg-[#00A97F] text-white text-[13px] font-bold px-4 py-1.5 rounded-full shadow-sm">
              Save 40%
            </div>
            
            <h3 className="text-[32px] font-bold text-white mb-4">Annual</h3>
            <p className="text-[16px] text-slate-300 mb-12 max-w-[280px]">12-month plan. Best value for year-round revision.</p>
            
            <div className="flex items-end gap-2 mb-2">
              <span className="text-[64px] font-bold text-white leading-none tracking-tight">£15</span>
              <span className="text-[16px] text-slate-300 mb-2 font-medium">/ mo</span>
            </div>
            <p className="text-[14px] text-slate-400 mb-12 font-medium">£180 billed yearly</p>

            <div className="mt-auto">
              <button className="w-full py-4 bg-white hover:bg-gray-50 text-black font-bold rounded-full mb-4 transition-colors text-[16px] shadow-lg shadow-black/10">
                Start for Free
              </button>
              <p className="text-[13px] text-slate-400 text-center font-medium">Always free to start. No credit card required.</p>
            </div>
            
            {/* Background Glow */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-slate-600 rounded-full blur-[100px] opacity-20 pointer-events-none"></div>
          </div>

        </div>

        {/* School Plan (Full Width Banner) */}
        <div className="w-full max-w-[1020px] mx-auto bg-white/60 backdrop-blur-md rounded-[32px] p-10 border border-white shadow-[0_8px_30px_rgb(0,0,0,0.02)] flex flex-col md:flex-row items-center justify-between text-center md:text-left hover:shadow-[0_12px_40px_rgb(0,0,0,0.04)] transition-all">
          <div>
            <h3 className="text-[28px] font-bold text-black leading-tight mb-2">
              Interested for your school or classroom?
            </h3>
            <p className="text-[16px] text-gray-500">Contact us to get enterprise pricing and implementation support.</p>
          </div>
          <div className="mt-6 md:mt-0 flex-shrink-0">
            <a href="mailto:contact@boostai.com" className="inline-block bg-[#3B82F6] hover:bg-blue-600 text-white font-bold text-[16px] py-4 px-8 rounded-full shadow-[0_4px_12px_rgba(59,130,246,0.3)] transition-all">
              contact@boostai.com
            </a>
          </div>
        </div>

      </div>
    </section>
  );
}
