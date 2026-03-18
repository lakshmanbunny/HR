import React from 'react';

const Hero = () => {

    return (
        <section className="flex flex-col items-center text-center py-10 md:py-16 px-6 max-w-4xl mx-auto">
            <h1 className="text-3xl md:text-5xl font-bold tracking-tight text-[#1A1A1A] mb-4">
                AI Recruitment Intelligence
            </h1>
            <p className="text-base md:text-lg text-gray-500 max-w-2xl leading-relaxed">
                Accelerate your hiring with deep-context candidate evaluation grounded in real-world GitHub evidence and technical intelligence.
            </p>
        </section>
    );
};

export default Hero;
