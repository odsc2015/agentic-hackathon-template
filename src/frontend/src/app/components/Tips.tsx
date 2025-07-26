'use client';

import React, { useState } from 'react';

const defaultTip = `During this phase, your partner might experience increased sensitivity and emotional fluctuations. Offer extra support and understanding, and be patient with any mood swings. Consider planning relaxing activities together, such as a quiet evening at home or a gentle walk in nature. Avoid stressful situations or conflicts, and communicate openly and calmly.`;

export default function Tips() {
  const [input, setInput] = useState('');
  const [generatedTip, setGeneratedTip] = useState(defaultTip);
  const [customTip, setCustomTip] = useState('');

  const handleGenerate = () => {
    setGeneratedTip(defaultTip);
    setCustomTip('');
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(customTip || generatedTip);
  };

  const handleShare = async () => {
    const text = customTip || generatedTip;
    if (navigator.share) {
      try {
        await navigator.share({ title: 'Supportive Tip', text });
      } catch (e) {}
    } else {
      alert('Sharing not supported.');
    }
  };

  return (
   <div className="min-h-screen w-full flex items-center justify-center bg-gray-50"> {/* 1. Center everything in the viewport */}
  <main className="bg-white rounded-xl shadow-md px-6 py-12 max-w-5xl w-full flex flex-col"> {/* 2. Constrain and center content */}
    <h1 className="text-3xl font-bold mb-2 text-black text-left">Support your partner</h1>
    <p className="mb-8 text-black text-left">
      Generate supportive tips and insights for your partner based on your cycle data. Customize and share information to foster understanding and empathy.
    </p>
    <section className="mb-10 w-full">
      <h2 className="text-xl font-semibold mb-2 text-black text-center">Generate tips</h2>
      <input
        className="w-full border border-gray-300 rounded-md px-3 py-2 mb-4 focus:outline-none focus:ring focus:border-blue-400 transition text-black"
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder=""
      />
      <div className="flex justify-center">
        <button
          className="bg-sky-400 hover:bg-sky-500 text-black rounded-md px-6 py-2 font-medium transition"
          onClick={handleGenerate}
        >
          Generate tips
        </button>
      </div>
    </section>
    <section className="w-full">
      <h2 className="text-xl font-semibold mb-2 text-black text-left">Generated tips</h2>
      <p className="mb-4 text-black text-center">
        {generatedTip}
      </p>
      <textarea
        className="w-full h-24 border border-gray-300 rounded-md px-3 py-2 mb-3 resize-none focus:outline-none focus:ring focus:border-blue-400 transition text-black"
        value={customTip}
        onChange={(e) => setCustomTip(e.target.value)}
        placeholder=""
      />
      <div className="flex space-x-3 justify-center">
        <button
          className="bg-gray-200 hover:bg-gray-300 text-black rounded-md px-4 py-2 font-medium transition"
          onClick={handleCopy}
        >
          Copy
        </button>
        <button
          className="bg-sky-400 hover:bg-sky-500 text-black rounded-md px-4 py-2 font-medium transition"
          onClick={handleShare}
        >
          Share
        </button>
      </div>
    </section>
  </main>
</div>
  );
}
