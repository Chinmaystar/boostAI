import './landing.css';
import logoImg from '../assets/logo.avif';

export default function LandingPage() {
    return (
        <div className="landing">
            {/* ===== Navbar ===== */}
            <nav className="navbar" id="navbar">
                <a href="/" className="navbar__logo" aria-label="BoostAI Home">
                    <img
                        src={logoImg}
                        alt="BoostAI logo"
                        className="navbar__logo-icon"
                        width="160"
                        height="160"
                    />
                    <span className="navbar__brand">BoostAI</span>
                </a>
            </nav>

            {/* ===== Main Content Wrapper ===== */}
            <div className="flex flex-col gap-8">
                {/* ===== Hero Section ===== */}
                <section className="hero" id="hero">
                    <div className="flex flex-col gap-4 text-left max-w-[900px]">
                        <h1 className="hero__title">
                            The all-in-one study
                            <br />
                            partner for your course
                        </h1>
                        <p className="hero__subtitle">
                            Choose where you're studying and start learning for free.
                        </p>
                    </div>
                </section>

                {/* ===== Category Cards ===== */}
                <section className="w-full max-w-[1200px] mx-auto px-6 pb-32 grid grid-cols-1 md:grid-cols-2 gap-8 lg:gap-12" id="categories">
                    
                    {/* School Card (Light Theme) */}
                    <a href="/school" className="group relative bg-white/90 backdrop-blur-md rounded-[40px] p-10 lg:p-12 overflow-hidden shadow-[0_8px_30px_rgb(0,0,0,0.04)] hover:shadow-[0_20px_40px_rgb(0,0,0,0.12)] hover:-translate-y-2 transition-all duration-500 border border-white flex flex-col min-h-[500px]">
                        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-yellow-200/40 rounded-full blur-[120px] -z-10 group-hover:bg-yellow-300/40 transition-colors duration-500"></div>
                        
                        <div className="relative z-10">
                            <span className="inline-block px-4 py-1.5 bg-yellow-100 text-yellow-800 font-bold text-[13px] rounded-full mb-6 shadow-sm border border-yellow-200">
                                GCSE to IB
                            </span>
                            <h2 className="text-[40px] font-bold tracking-tight text-black mb-4 leading-tight">I'm at school</h2>
                            <p className="text-[17px] text-gray-600 mb-10 max-w-[80%]">
                                Master your GCSE, A-Level, IGCSE, IAL and IB courses with interactive AI prep.
                            </p>
                            <span className="inline-flex items-center gap-2 px-8 py-4 bg-black text-white font-bold rounded-full hover:bg-gray-800 transition-colors shadow-lg group-hover:shadow-xl">
                                Go to BoostAI Exams
                                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                            </span>
                        </div>
                        
                        <div className="mt-auto w-full pt-12 flex items-end justify-center perspective-[1000px]">
                            <img
                                src="/new_school_mockup.png"
                                alt="BoostAI school exam interface"
                                className="w-[90%] max-w-[400px] object-cover object-top rounded-t-2xl shadow-[0_-10px_40px_rgba(0,0,0,0.1)] group-hover:-translate-y-4 group-hover:scale-105 transition-all duration-700 ease-out"
                                loading="lazy"
                            />
                        </div>
                    </a>

                    {/* University Card (Dark Theme) */}
                    <a href="/university" className="group relative bg-[#0F172A] rounded-[40px] px-10 pt-12 lg:px-12 lg:pt-14 overflow-hidden shadow-[0_20px_50px_rgba(15,23,42,0.2)] hover:shadow-[0_30px_60px_rgba(15,23,42,0.4)] hover:-translate-y-2 transition-all duration-500 border border-slate-800 flex flex-col h-full">
                        <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-blue-600/20 rounded-full blur-[120px] -z-10 group-hover:bg-blue-500/30 transition-colors duration-500"></div>
                        
                        <div className="relative z-10 flex-shrink-0">
                            <span className="inline-block px-4 py-1.5 bg-blue-500/20 text-blue-300 font-bold text-[13px] rounded-full mb-6 shadow-sm border border-blue-500/30">
                                Undergraduate & Postgrad
                            </span>
                            <h2 className="text-[40px] font-bold tracking-tight text-white mb-4 leading-tight">I'm at university</h2>
                            <p className="text-[17px] text-slate-300 mb-10 max-w-[90%]">
                                Effortlessly organise modules, understand complex topics, and ace your exams.
                            </p>
                            <span className="inline-flex items-center gap-2 px-8 py-4 bg-white text-black font-bold rounded-full hover:bg-gray-100 transition-colors shadow-lg group-hover:shadow-xl">
                                Go to BoostAI Open
                                <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                                </svg>
                            </span>
                        </div>
                        
                        <div className="mt-auto w-full pt-12 flex items-end justify-center perspective-[1000px]">
                            <img
                                src="/new_univ_mockup.png"
                                alt="BoostAI university interface"
                                className="w-[90%] max-w-[400px] object-cover object-top rounded-t-2xl shadow-[0_-10px_40px_rgba(0,0,0,0.3)] group-hover:-translate-y-4 group-hover:scale-105 transition-all duration-700 ease-out"
                                loading="lazy"
                            />
                        </div>
                    </a>

                </section>
            </div>
        </div>
    );
}
