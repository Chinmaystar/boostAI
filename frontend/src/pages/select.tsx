import { useState } from 'react';

export default function SelectPage() {
  const [selection, setSelection] = useState<'school' | 'univ' | null>(null);

  const handleContinue = () => {
    if (selection) {
      window.location.href = `/login?role=${selection}`;
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col items-center pt-24 pb-20 px-4 font-sans text-center overflow-y-auto">
      
      {/* Headings */}
      <h1 className="text-[40px] md:text-[46px] font-bold tracking-tight text-[#0F172A] leading-[1.1] mb-5 max-w-[600px]">
        The all-in-one study partner for your course
      </h1>
      <p className="text-[20px] text-gray-500 mb-12 font-medium">
        Choose where you're studying and start learning for free.
      </p>

      {/* Cards Container */}
      <div className="flex flex-col md:flex-row gap-6 w-full max-w-[800px]">
        
        {/* School Card */}
        <div 
          onClick={() => setSelection('school')}
          className={`flex-1 relative border-[1.5px] rounded-[24px] p-4 pb-6 cursor-pointer transition-all duration-200 text-left bg-white overflow-hidden flex flex-col
            ${selection === 'school' ? 'border-blue-500 shadow-sm ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300'}`}
        >
           {/* Mockup image top half */}
           <div className="w-full flex justify-center mb-5 rounded-xl overflow-hidden pt-4 px-4 h-[160px] relative">
             <div className="absolute inset-0 bg-gray-50/50"></div>
             <img src="/new_school_mockup.png" alt="School Interface" className="w-[95%] object-cover object-top rounded-t-lg shadow-sm border border-gray-200/60 relative z-10" />
           </div>

           {/* Content bottom half */}
           <div className="flex items-center gap-3 px-2">
             {/* Radio Button */}
             <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors
                ${selection === 'school' ? 'border-blue-500 bg-blue-500' : 'border-gray-300'}`}>
                {selection === 'school' && <div className="w-2 h-2 bg-white rounded-full"></div>}
             </div>
             <div>
               <h3 className="text-[18px] font-semibold text-gray-900 leading-none">I'm at school</h3>
               <p className="text-[14px] text-gray-500 mt-1.5">GCSE, A-Level, IGCSE...</p>
             </div>
           </div>
        </div>

        {/* University Card */}
        <div 
          onClick={() => setSelection('univ')}
          className={`flex-1 relative border-[1.5px] rounded-[24px] p-4 pb-6 cursor-pointer transition-all duration-200 text-left bg-white overflow-hidden flex flex-col
            ${selection === 'univ' ? 'border-blue-500 shadow-sm ring-1 ring-blue-500' : 'border-gray-200 hover:border-gray-300'}`}
        >
           {/* Mockup image top half */}
           <div className="w-full flex justify-center mb-5 rounded-xl overflow-hidden pt-4 px-4 h-[160px] relative">
             <div className="absolute inset-0 bg-pink-50/40"></div>
             <img src="/new_univ_mockup.png" alt="University Interface" className="w-[95%] object-cover object-top rounded-t-lg shadow-sm border border-gray-200/60 relative z-10" />
           </div>

           {/* Content bottom half */}
           <div className="flex items-center gap-3 px-2">
             {/* Radio Button */}
             <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 transition-colors
                ${selection === 'univ' ? 'border-blue-500 bg-blue-500' : 'border-gray-300'}`}>
                {selection === 'univ' && <div className="w-2 h-2 bg-white rounded-full"></div>}
             </div>
             <div>
               <h3 className="text-[18px] font-semibold text-gray-900 leading-none">I'm at university</h3>
               <p className="text-[14px] text-gray-500 mt-1.5">University courses</p>
             </div>
           </div>
        </div>

      </div>

      {/* Continue Button */}
      <div className="w-full flex justify-center mt-12 pb-20">
        <button 
          onClick={handleContinue}
          disabled={!selection}
          className={`w-[90%] max-w-[400px] py-4 rounded-2xl text-lg font-bold transition-all duration-200
            ${selection !== null ? '!bg-slate-900 hover:!bg-black !text-white shadow-xl transform hover:-translate-y-1' : '!bg-gray-200 !text-gray-500 cursor-not-allowed'}`}
        >
          Continue
        </button>
      </div>

    </div>
  );
}
