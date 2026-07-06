import React from "react";

export default function SchoolPricing() {
  return (
    <section
      className="w-full bg-[#292524]"
      style={{
        paddingLeft: "160px",
        paddingRight: "160px",
        paddingTop: "80px",
        paddingBottom: "120px",
      }}
    >
      <div className="max-w-[1080px] mx-auto">
        {/* Header */}
        <div className="mb-20">
          <h2 className="text-[48px] md:text-[56px] leading-[1.1] font-bold tracking-tight text-white max-w-[600px] mb-4">
            Personalised tutoring at a fraction of the cost
          </h2>
          <p className="text-[18px] text-gray-300">
            From £24.99/month, a fraction of the cost of private tutoring
            <sup className="text-sm">1</sup>.
          </p>
        </div>

        {/* Chart & Pricing Details */}
        <div className="flex flex-col md:flex-row items-end gap-16 md:gap-32">
          {/* Bar Chart */}
          <div className="flex items-end gap-2">
            {/* Private Tutoring Bar */}
            <div className="flex flex-col items-center">
              <div className="w-[120px] h-[320px] bg-[#2244C8] rounded-t-sm"></div>
              <div className="text-center mt-4">
                <p className="text-[14px] text-blue-300 font-medium">
                  Private tutoring
                </p>
                <p className="text-[14px] text-blue-300">
                  ~£96/month<sup className="text-xs">2</sup>
                </p>
              </div>
            </div>

            {/* BoostAI Bar */}
            <div className="flex flex-col items-center">
              <div className="w-[120px] h-[80px] bg-[#FFA6D9] rounded-t-sm"></div>
              <div className="text-center mt-4">
                <p className="text-[14px] text-white font-bold">BoostAI</p>
                <p className="text-[14px] text-white font-bold">£24.99/month</p>
              </div>
            </div>
          </div>

          {/* Right Text */}
          <div className="mb-12 text-center md:text-left">
            <h3 className="text-[48px] md:text-[64px] font-bold text-white leading-[1.1] mb-4">
              From <br /> £24.99/mo
            </h3>
            <p className="text-[18px] text-gray-300 max-w-[280px] mx-auto md:mx-0">
              a fraction of the cost of private tutoring
              <sup className="text-sm">2</sup>
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
