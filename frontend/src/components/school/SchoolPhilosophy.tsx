import React, { useState } from "react";

export default function SchoolPhilosophy() {
  const [openSection, setOpenSection] = useState<string>("learning");

  const toggleSection = (section: string) => {
    setOpenSection(openSection === section ? "" : section);
  };

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
      <div className="max-w-[1080px] mx-auto flex flex-col md:flex-row gap-16 md:gap-32">
        {/* Left Column - Heading */}
        <div className="md:w-1/3">
          <h2 className="text-[48px] leading-[1.1] font-bold tracking-tight text-white">
            Our philosophy on AI is a little different
          </h2>
        </div>

        {/* Right Column - Accordion */}
        <div className="md:w-2/3 flex flex-col">
          {/* Item 1 */}
          <div className="border-b border-blue-800 pb-6 mb-6">
            <button
              onClick={() => toggleSection("learning")}
              className="w-full flex justify-between items-center text-left"
            >
              <h3 className="text-[28px] font-bold text-white">
                Made for learning
              </h3>
              <svg
                className={`w-6 h-6 text-white transition-transform ${openSection === "learning" ? "rotate-180" : ""}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {openSection === "learning" && (
              <div className="mt-6 text-[18px] text-gray-300 flex flex-col gap-6 pr-12">
                <p>
                  BoostAI helps you learn, not by just telling you the answers,
                  but by asking you the right questions.
                </p>
                <p>
                  BoostAI will not write entire essays for you, or instantly
                  give you the answer to assignments, but it will guide you to
                  the answers and help you plan your essays using your materials
                  as context.
                </p>
                <p>
                  BoostAI automates your mundane tasks, so you can focus on
                  doing better.
                </p>
              </div>
            )}
          </div>

          {/* Item 2 */}
          <div className="border-b border-blue-800 pb-6 mb-6">
            <button
              onClick={() => toggleSection("sustainability")}
              className="w-full flex justify-between items-center text-left"
            >
              <h3 className="text-[28px] font-bold text-white">
                Made with sustainability in mind
              </h3>
              <svg
                className={`w-6 h-6 text-white transition-transform ${openSection === "sustainability" ? "rotate-180" : ""}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {openSection === "sustainability" && (
              <div className="mt-6 text-[18px] text-gray-300 pr-12">
                <p>
                  We believe in building technology that minimizes our
                  environmental footprint and promotes sustainable learning
                  practices for the future.
                </p>
              </div>
            )}
          </div>

          {/* Item 3 */}
          <div className="pb-6">
            <button
              onClick={() => toggleSection("privacy")}
              className="w-full flex justify-between items-center text-left"
            >
              <h3 className="text-[28px] font-bold text-white">
                Made for privacy
              </h3>
              <svg
                className={`w-6 h-6 text-white transition-transform ${openSection === "privacy" ? "rotate-180" : ""}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            </button>

            {openSection === "privacy" && (
              <div className="mt-6 text-[18px] text-gray-300 pr-12">
                <p>
                  Your data belongs to you. We employ industry-leading
                  encryption and strict privacy protocols to ensure your
                  learning materials remain secure and confidential.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
