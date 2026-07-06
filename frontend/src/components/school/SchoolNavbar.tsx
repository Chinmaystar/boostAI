import React from "react";
import logoImg from "../../assets/logo.avif";

export default function SchoolNavbar() {
  return (
    <div className="w-full sticky top-0 z-50 bg-white/70 backdrop-blur-md border-b border-[#E5E7EB]/50" style={{ paddingLeft: "160px", paddingRight: "160px" }}>
      <div className="flex items-center justify-between h-[95px]">
        {/* Logo */}
        <a href="/" className="flex items-center gap-2 shrink-0">
          <img
            src={logoImg}
            alt="BoostAI logo"
            className="navbar__logo-icon"
            width="80"
            height="80"
          />
          <span className="text-2xl font-extrabold tracking-tight text-black">
            BoostAI
          </span>
        </a>

        {/* Navigation Links */}
        <div className="hidden lg:flex items-center gap-8">
          <a
            href="#"
            className="text-base text-[#171717] hover:text-black transition-all whitespace-nowrap"
          >
            Our Story
          </a>
          <a
            href="#"
            className="text-base text-[#171717] hover:text-black transition-all whitespace-nowrap"
          >
            Blog
          </a>
          <a
            href="#"
            className="text-base text-[#171717] hover:text-black transition-all whitespace-nowrap"
          >
            Past Papers
          </a>
          <a
            href="#"
            className="text-base text-[#171717] hover:text-black transition-all whitespace-nowrap"
          >
            Teachers
          </a>
          <a
            href="#"
            className="text-base text-[#171717] hover:text-black transition-all whitespace-nowrap"
          >
            Pricing
          </a>
          <a
            href="#"
            className="text-base text-[#171717] hover:text-black transition-all whitespace-nowrap"
          >
            Updates
          </a>
        </div>

        {/* Auth Buttons */}
        <div className="flex items-center gap-6 shrink-0">
          <a
            href="/select"
            className="text-base text-[#171717] hover:text-black transition-all whitespace-nowrap"
          >
            Login
          </a>
          <a
            href="/select"
            className="whitespace-nowrap rounded-full border border-[#292524] text-[18px] leading-[28px] text-[#292524] hover:bg-gray-50 transition-all"
            style={{ padding: "12px 24px" }}
          >
            Sign up for Free
          </a>
        </div>
      </div>
    </div>
  );
}
