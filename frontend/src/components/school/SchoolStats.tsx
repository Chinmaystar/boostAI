import React from "react";

export default function SchoolStats() {
  return (
    <section
      className="w-full bg-[#292524]"
      style={{
        paddingLeft: "160px",
        paddingRight: "160px",
        paddingTop: "100px",
        paddingBottom: "100px",
      }}
    >
      <div className="max-w-[1080px] mx-auto">
        <h2 className="text-[48px] md:text-[56px] leading-[1.05] font-bold tracking-tight text-white max-w-[800px]">
          74% of surveyed students improved their grades while using BoostAI.
        </h2>
        <a
          href="#"
          className="inline-block text-white text-[18px] font-medium underline underline-offset-4 mt-8 hover:text-gray-300 transition-colors"
        >
          See our full GCSE 2025 results
        </a>
      </div>
    </section>
  );
}
