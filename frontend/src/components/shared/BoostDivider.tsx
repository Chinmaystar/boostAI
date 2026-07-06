import React from 'react';
import BoostLogo from './BoostLogo';
export default function BoostDivider() {
    return (
        <div className="w-full sticky top-[95px] z-40 flex items-center justify-center overflow-hidden shadow-sm" style={{ height: "48px", backgroundColor: "#3B82F6" }}>
            <div className="absolute inset-0 z-0" style={{
                background: "repeating-linear-gradient(-30deg, #3B82F6, #3B82F6 100px, #8bb8ff 100px, #8bb8ff 160px)"
            }}></div>
            
            {/* Center block to hide stripes under text */}
            <div className="z-0 absolute inset-0 flex justify-center">
                <div className="w-[60%] sm:w-[50%] md:w-[40%] lg:w-[30%] h-full bg-[#3B82F6]"></div>
            </div>

            {/* Gradient fade to blend the solid block with the stripes */}
            <div className="z-0 absolute inset-0 flex justify-center pointer-events-none">
                <div className="w-[70%] sm:w-[60%] md:w-[50%] lg:w-[40%] h-full bg-gradient-to-r from-transparent via-[#3B82F6] to-transparent"></div>
            </div>

            <div className="z-10 flex items-center gap-2 text-white font-bold text-xl px-4 sm:px-8 h-full bg-[#3B82F6]">
                <BoostLogo className="w-8 h-8 text-white" />
                <span>BoostAI</span>
            </div>
        </div>
    );
}
