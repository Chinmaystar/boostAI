import React from "react";

export default function UnivFooter() {
  return (
    <footer
      className="w-full bg-[#252323] pt-32 pb-16"
      style={{ paddingLeft: "120px", paddingRight: "120px" }}
    >
      <div className="max-w-[1200px] mx-auto flex flex-col items-center">
        {/* Main Header */}
        <h2 className="text-[64px] md:text-[80px] leading-[1.05] font-bold tracking-tight text-white text-center mb-32 max-w-[800px]">
          Built for every learner
        </h2>

        {/* Bottom Bar */}
        <div className="w-full flex flex-col md:flex-row items-center justify-between gap-8 md:gap-12 text-[#9A9898] text-[13px]">
          {/* Disclaimer */}
          <div className="md:w-1/3 text-right md:text-left leading-relaxed">
            <p>
              IBO, AQA, Pearson, OCR or WJEC were not involved in the production
              of, and do not endorse, the resources or AI tutoring provided on
              the BoostAI Platform.
            </p>
          </div>

          {/* Logo Placeholder */}
          <div className="flex-shrink-0 text-white font-bold text-2xl tracking-tighter italic">
            BoostAI
          </div>

          {/* Links */}
          <div className="md:w-auto flex flex-wrap justify-center gap-6 md:gap-8 text-[13px]">
            <a href="#" className="hover:text-white transition-colors">
              Cookies
            </a>
            <a href="#" className="hover:text-white transition-colors">
              Privacy Policy
            </a>
            <a href="#" className="hover:text-white transition-colors">
              Terms of Service
            </a>
            <a href="#" className="hover:text-white transition-colors">
              Safety
            </a>
            <a href="#" className="hover:text-white transition-colors">
              Bursary
            </a>
            <a href="#" className="hover:text-white transition-colors">
              Cost comparison
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
