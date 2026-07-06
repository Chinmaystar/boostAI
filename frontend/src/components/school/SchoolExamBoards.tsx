import React, { useState } from "react";

export default function SchoolExamBoards() {
  const [activeTab, setActiveTab] = useState("GCSE");
  
  const tabs = ["GCSE", "IGCSE", "A-Level", "IB"];

  return (
    <section className="w-full pb-32" style={{ paddingLeft: "160px", paddingRight: "160px", paddingTop: "80px" }}>
      <div className="max-w-[1080px] mx-auto">
        
        {/* Header & Tabs */}
        <div className="flex flex-col md:flex-row md:items-center justify-between mb-16">
          <h2 className="text-[48px] leading-[1.1] font-bold tracking-[-0.02em] text-black">
            Matched to your exam board
          </h2>
          
          <div className="flex items-center bg-[#F4F4F5] rounded-lg p-1 mt-6 md:mt-0">
            {tabs.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-2 rounded-md text-[15px] font-semibold transition-all ${
                  activeTab === tab
                    ? "bg-white text-black shadow-sm"
                    : "text-blue-300 hover:text-gray-700"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Exam Boards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-x-8 gap-y-12">
          
          {/* AQA Column */}
          <div>
            <h3 className="text-[18px] font-bold text-[#171717] mb-6">AQA</h3>
            <ul className="flex flex-col gap-3">
              {["Biology", "Business", "Chemistry", "Citizenship", "Computer Science", "Design & Technology", "Economics", "English", "English Literature", "Food and Nutrition", "Geography", "History", "Maths", "Media Studies", "Physical Education", "Physics", "Psychology", "Religious Education", "Sociology"].map(subject => (
                <li key={subject} className="text-[14px] text-[#525252] hover:text-black cursor-pointer transition-colors">
                  {subject}
                </li>
              ))}
            </ul>
          </div>

          {/* Edexcel Column */}
          <div>
            <h3 className="text-[18px] font-bold text-[#171717] mb-6">Edexcel</h3>
            <ul className="flex flex-col gap-3">
              {["Biology", "Business", "Chemistry", "Citizenship", "Computer Science", "Design & Technology", "English Literature", "Geography", "History", "Maths", "Physical Education", "Physics", "Psychology", "Religious Education", "Statistics"].map(subject => (
                <li key={subject} className="text-[14px] text-[#525252] hover:text-black cursor-pointer transition-colors">
                  {subject}
                </li>
              ))}
            </ul>
          </div>

          {/* OCR Column */}
          <div>
            <h3 className="text-[18px] font-bold text-[#171717] mb-6">OCR</h3>
            <ul className="flex flex-col gap-3">
              {["Biology", "Business", "Chemistry", "Citizenship", "Computer Science", "Economics", "Geography", "History", "Maths", "Physical Education", "Physics"].map(subject => (
                <li key={subject} className="text-[14px] text-[#525252] hover:text-black cursor-pointer transition-colors">
                  {subject}
                </li>
              ))}
            </ul>
          </div>

          {/* WJEC Column */}
          <div>
            <h3 className="text-[18px] font-bold text-[#171717] mb-6">WJEC</h3>
            <ul className="flex flex-col gap-3">
              {["Biology", "Business", "Chemistry", "Computer Science", "Design & Technology", "Film Studies", "Food and Nutrition", "Geography", "History", "Maths", "Physical Education", "Physics", "Religious Education", "Sociology"].map(subject => (
                <li key={subject} className="text-[14px] text-[#525252] hover:text-black cursor-pointer transition-colors">
                  {subject}
                </li>
              ))}
            </ul>
          </div>

        </div>

      </div>
    </section>
  );
}
