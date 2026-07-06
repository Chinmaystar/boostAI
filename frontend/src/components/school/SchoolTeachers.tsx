import React, { useState } from "react";

export default function SchoolTeachers() {
  const [activeTab, setActiveTab] = useState("STEM");
  const tabs = ["STEM", "Humanities"];

  return (
    <section
      className="w-full bg-[#292524]"
      style={{
        paddingLeft: "160px",
        paddingRight: "160px",
        paddingTop: "120px",
        paddingBottom: "120px",
      }}
    >
      <div className="max-w-[1200px] mx-auto">
        {/* Header & Toggle */}
        <div className="flex flex-col items-start md:items-center text-left md:text-center mb-16">
          <h2 className="text-[48px] md:text-[56px] leading-[1.1] font-bold tracking-tight text-white mb-4">
            Reviewed by experienced teachers
          </h2>
          <p className="text-[20px] text-gray-300 mb-10">
            Experts who have taught and even examined for your subject
          </p>

          <div className="inline-flex items-center bg-[#1c1917] rounded-full p-1.5 shadow-inner border border-white/10">
            {tabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-10 py-2.5 rounded-full text-[15px] font-bold transition-all duration-300 ${
                  activeTab === tab
                    ? "bg-white text-black shadow-[0_2px_10px_rgba(0,0,0,0.2)]"
                    : "text-stone-400 hover:text-white hover:bg-white/5"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Teachers Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1 */}
          <div className="bg-white rounded-xl overflow-hidden flex flex-col">
            <div className="bg-blue-50 py-4 px-6">
              <h3 className="text-[18px] font-bold text-black">Biology</h3>
            </div>
            <div
              className="h-[240px] bg-gray-200 bg-cover bg-center"
              style={{
                backgroundImage:
                  "url('https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=400&auto=format&fit=crop&grayscale=1')",
              }}
            ></div>
            <div className="p-6 flex flex-col flex-grow">
              <h4 className="text-[18px] font-bold text-black mb-4">
                Ms. Leslie
              </h4>
              <ul className="text-[13px] text-gray-600 flex flex-col gap-2 list-disc pl-4 marker:text-blue-200">
                <li>20+ years teaching experience</li>
                <li>15 years as a senior examiner</li>
                <li>
                  MSc Education Policy and International Development, Bristol
                  University
                </li>
                <li>PGCE Secondary Sciences, Exeter</li>
              </ul>
            </div>
          </div>

          {/* Card 2 */}
          <div className="bg-white rounded-xl overflow-hidden flex flex-col">
            <div className="bg-blue-50 py-4 px-6">
              <h3 className="text-[18px] font-bold text-black">Chemistry</h3>
            </div>
            <div
              className="h-[240px] bg-gray-200 bg-cover bg-center"
              style={{
                backgroundImage:
                  "url('https://images.unsplash.com/photo-1580894732444-8ecded7900cd?q=80&w=400&auto=format&fit=crop')",
              }}
            ></div>
            <div className="p-6 flex flex-col flex-grow">
              <h4 className="text-[18px] font-bold text-black mb-4">
                Ms. Temple
              </h4>
              <ul className="text-[13px] text-gray-600 flex flex-col gap-2 list-disc pl-4 marker:text-blue-200">
                <li>25+ years teaching experience</li>
                <li>Educator and curriculum specialist</li>
                <li>
                  Worked in top-performing schools and multi-academy trusts
                </li>
                <li>Taught STEM at GCSE and A Level across</li>
              </ul>
            </div>
          </div>

          {/* Card 3 */}
          <div className="bg-white rounded-xl overflow-hidden flex flex-col">
            <div className="bg-blue-50 py-4 px-6">
              <h3 className="text-[18px] font-bold text-black">
                Computer Science
              </h3>
            </div>
            <div
              className="h-[240px] bg-gray-200 bg-cover bg-center"
              style={{
                backgroundImage:
                  "url('https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=400&auto=format&fit=crop')",
              }}
            ></div>
            <div className="p-6 flex flex-col flex-grow">
              <h4 className="text-[18px] font-bold text-black mb-4">
                Mr. Spear
              </h4>
              <ul className="text-[13px] text-gray-600 flex flex-col gap-2 list-disc pl-4 marker:text-blue-200">
                <li>13+ years teaching experience</li>
                <li>PGCE</li>
                <li>First-class honours degree</li>
                <li>Head of Department</li>
                <li>Marked for WJEC, OCR, Edexcel, and AQA</li>
              </ul>
            </div>
          </div>

          {/* Card 4 */}
          <div className="bg-white rounded-xl overflow-hidden flex flex-col">
            <div className="bg-blue-50 py-4 px-6">
              <h3 className="text-[18px] font-bold text-black">Physics</h3>
            </div>
            <div
              className="h-[240px] bg-gray-200 bg-cover bg-center"
              style={{
                backgroundImage:
                  "url('https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=400&auto=format&fit=crop')",
              }}
            ></div>
            <div className="p-6 flex flex-col flex-grow">
              <h4 className="text-[18px] font-bold text-black mb-4">Mr. Ali</h4>
              <ul className="text-[13px] text-gray-600 flex flex-col gap-2 list-disc pl-4 marker:text-blue-200">
                <li>12+ years teaching experience</li>
                <li>Assessment Lead Teacher</li>
                <li>Curriculum resource developer</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
