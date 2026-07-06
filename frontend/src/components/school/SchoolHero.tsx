import React from "react";

export default function SchoolHero() {
  return (
    <section className="w-full" style={{ paddingLeft: "160px", paddingRight: "160px", paddingTop: "80px", paddingBottom: "80px" }}>
      <div className="max-w-[700px]">
        <h1 className="text-[56px] leading-[1.1] font-extrabold tracking-[-0.02em] text-black">
          The first AI tutor for GCSE, A-Level and IB<sup className="text-[24px] align-super">1</sup>
        </h1>
        <p className="text-[18px] leading-[28px] max-w-[560px]" style={{ color: "#171717", opacity: 0.8, marginTop: "20px" }}>
          Practice questions built like real exams. Your marks, explained. Everything you need to improve, all in one place.
        </p>
        <a
          href="#"
          className="inline-block rounded-full font-medium hover:bg-[#333] transition-all"
          style={{ padding: "14px 32px", backgroundColor: "#1a1a1a", color: "#ffffff", fontSize: "18px", lineHeight: "28px", marginTop: "28px" }}
        >
          Sign up for Free
        </a>
      </div>
    </section>
  );
}
