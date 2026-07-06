import React from "react";
import Masonry from "../shared/Masonry";

export default function SchoolTestimonials() {
  const items = [
    {
      id: "1",
      height: 440,
      content: (
        <div className="bg-[#F4F6FA] rounded-[24px] p-6 md:p-8 h-full flex flex-col relative overflow-hidden transition-all hover:shadow-md border border-gray-100">
           <div className="mt-auto">
             <h3 className="text-[28px] font-bold leading-tight mb-2 text-black">Easy to<br/>understand</h3>
             <div className="flex text-blue-500 mb-4 text-xl">★★★★★</div>
             <p className="text-[14px] md:text-[15px] text-gray-600 leading-relaxed">It's great that you can receive feedback for exam questions tailored to your exam board.</p>
           </div>
        </div>
      )
    },
    {
      id: "2",
      height: 300,
      content: (
        <div className="bg-gray-200 rounded-[24px] h-full relative overflow-hidden bg-cover bg-center shadow-sm" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1517486808906-6ca8b3f04846?q=80&w=600&auto=format&fit=crop')" }}>
        </div>
      )
    },
    {
      id: "3",
      height: 440,
      content: (
        <div className="bg-[#F4F6FA] rounded-[24px] p-6 md:p-8 h-full flex flex-col relative overflow-hidden transition-all hover:shadow-md border border-gray-100">
          <div>
            <p className="text-[13px] md:text-[14px] font-semibold text-gray-500 uppercase tracking-wider mb-1">Physics Student</p>
            <p className="text-[15px] md:text-[16px] font-bold text-black mb-6">Leo</p>
          </div>
          <div className="mt-auto">
            <h3 className="text-[28px] md:text-[32px] font-bold leading-tight mb-4 text-black">Boosted<br/>my<br/>confidence</h3>
            <div className="flex text-blue-500 text-xl mb-4">★★★★★</div>
            <p className="text-[14px] md:text-[15px] text-gray-600 leading-relaxed">It has helped me to greater understand the content for my physics exam. The tutor feature is really helpful for boosting confidence going into this exam.</p>
          </div>
        </div>
      )
    },
    {
      id: "4",
      height: 340,
      content: (
        <div className="bg-gray-300 rounded-[24px] h-full relative overflow-hidden bg-cover bg-center shadow-sm" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1529333166437-7750a6dd5a70?q=80&w=600&auto=format&fit=crop')" }}>
           <div className="absolute inset-0 flex items-center justify-center bg-black/5 hover:bg-black/10 transition-colors">
             <div className="w-14 h-14 bg-white/95 rounded-full flex items-center justify-center pl-1 cursor-pointer shadow-lg hover:scale-110 transition-transform">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="#3B82F6"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
             </div>
           </div>
        </div>
      )
    },
    {
      id: "5",
      height: 440,
      content: (
        <div className="bg-blue-600 rounded-[24px] p-6 md:p-8 h-full flex flex-col relative overflow-hidden transition-all hover:shadow-md shadow-[0_10px_30px_rgba(37,99,235,0.2)]">
          <div>
            <p className="text-[13px] md:text-[14px] font-semibold text-blue-200 uppercase tracking-wider mb-1">GCSE Student</p>
            <p className="text-[15px] md:text-[16px] font-bold text-white mb-6">Zane</p>
          </div>
          <div className="mt-auto">
            <h3 className="text-[28px] md:text-[32px] font-bold leading-tight mb-4 text-white">Amazing<br/>app</h3>
            <div className="flex text-yellow-400 text-xl mb-4">★★★★★</div>
            <p className="text-[14px] md:text-[15px] text-blue-50 leading-relaxed">The AI chatbot is extremely helpful and the walkthrough feature is great for learning new content - with the information being given to you bit by bit it really helps build knowledge.</p>
          </div>
        </div>
      )
    },
    {
      id: "6",
      height: 300,
      content: (
        <div className="bg-[#F4F6FA] rounded-[24px] p-6 md:p-8 h-full flex flex-col relative overflow-hidden transition-all hover:shadow-md border border-gray-100">
          <div>
            <p className="text-[13px] md:text-[14px] font-semibold text-gray-500 uppercase tracking-wider mb-1">GCSE Student</p>
            <p className="text-[15px] md:text-[16px] font-bold text-black">Ahmad</p>
          </div>
          <div className="mt-auto">
             <div className="flex text-blue-500 text-xl mb-4">★★★★★</div>
             <p className="text-[14px] md:text-[15px] text-gray-600 leading-relaxed">It's incredibly helpful. Highly recommend to everyone!</p>
          </div>
        </div>
      )
    },
    {
      id: "7",
      height: 480,
      content: (
        <div className="bg-gray-200 rounded-[24px] h-full relative overflow-hidden bg-cover bg-center shadow-sm" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1610484826967-09c5720778c7?q=80&w=600&auto=format&fit=crop')" }}>
           <div className="absolute inset-0 flex items-center justify-center bg-black/10 hover:bg-black/20 transition-colors">
             <div className="w-16 h-16 bg-white/95 rounded-full flex items-center justify-center pl-1 cursor-pointer shadow-lg hover:scale-110 transition-transform">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="#3B82F6"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
             </div>
           </div>
        </div>
      )
    },
    {
      id: "8",
      height: 300,
      content: (
        <div className="bg-[#F4F6FA] rounded-[24px] p-6 md:p-8 h-full flex flex-col relative overflow-hidden transition-all hover:shadow-md border border-gray-100">
          <div>
            <p className="text-[13px] md:text-[14px] font-semibold text-gray-500 uppercase tracking-wider mb-1">GCSE Student</p>
            <p className="text-[15px] md:text-[16px] font-bold text-black">Mano</p>
          </div>
          <div className="mt-auto">
             <div className="flex text-blue-500 text-xl mb-4">★★★★★</div>
             <p className="text-[14px] md:text-[15px] text-gray-600 leading-relaxed">It changed how I study completely.</p>
          </div>
        </div>
      )
    }
  ];

  return (
    <section className="w-full pb-32" style={{ paddingLeft: "160px", paddingRight: "160px", paddingTop: "80px" }}>
      <div className="max-w-[1200px] mx-auto">
        
        {/* Header */}
        <div className="mb-16">
          <h2 className="text-[48px] md:text-[56px] leading-[1.1] font-bold tracking-tight text-black mb-4">
            Loved by 300,000+ students
          </h2>
          <p className="text-[20px] text-gray-600">
            Here's what our students have to say.
          </p>
        </div>

        {/* Masonry Layout Container */}
        <div className="w-full" style={{ minHeight: '600px' }}>
          <Masonry 
            items={items} 
            ease="power3.out"
            duration={0.6}
            stagger={0.05}
            animateFrom="bottom"
            scaleOnHover={true}
            hoverScale={0.98}
            blurToFocus={true}
          />
        </div>
      </div>
    </section>
  );
}
