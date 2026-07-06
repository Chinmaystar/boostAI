import React, { useState } from "react";

export default function SchoolFAQs() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFaq = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  const faqs = [
    {
      question: "Is BoostAI specific to the GCSE and A-Level specification?",
      answer: "Yes, our content is tailored to major exam boards.",
    },
    {
      question: "How are answers marked on BoostAI?",
      answer: "Our AI uses official mark schemes to evaluate your answers.",
    },
    {
      question: "How does BoostAI help students prepare for exams?",
      answer:
        "By providing personalized feedback and targeted practice questions.",
    },
    {
      question: "What is the difference between BoostAI and BoostAI Exams?",
      answer:
        "BoostAI is for general learning, while BoostAI Exams focuses strictly on past paper practice.",
    },
    {
      question: "Does BoostAI cover everything for the exam?",
      answer:
        "We cover the vast majority of the core curriculum for the supported subjects.",
    },
    {
      question: "How do I cancel my subscription?",
      answer: "You can cancel anytime from your account settings.",
    },
    {
      question: "Does BoostAI get stuff wrong?",
      answer:
        "While highly accurate, our AI can occasionally make mistakes. Always cross-reference important concepts.",
    },
    {
      question: "Do you offer school subscriptions?",
      answer:
        "Yes, we offer bulk licensing and school-wide deployment options. Contact us for details.",
    },
  ];

  return (
    <section
      className="w-full bg-[#292524] text-white"
      style={{
        paddingLeft: "160px",
        paddingRight: "160px",
        paddingTop: "120px",
        paddingBottom: "120px",
      }}
    >
      <div className="max-w-[1200px] mx-auto flex flex-col md:flex-row gap-16 md:gap-32">
        {/* Left Column */}
        <div className="md:w-1/3">
          <h2 className="text-[48px] md:text-[56px] font-bold tracking-tight">
            FAQs
          </h2>
        </div>

        {/* Right Column */}
        <div className="md:w-2/3 flex flex-col">
          {faqs.map((faq, index) => (
            <div key={index} className="border-b border-blue-800">
              <button
                onClick={() => toggleFaq(index)}
                className="w-full py-6 flex justify-between items-center text-left hover:text-gray-300 transition-colors"
              >
                <span className="text-[20px] font-medium">{faq.question}</span>
                <svg
                  className={`w-5 h-5 transition-transform ${openIndex === index ? "rotate-180" : ""}`}
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

              {openIndex === index && (
                <div className="pb-6 text-blue-200 text-[16px] pr-8">
                  {faq.answer}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
