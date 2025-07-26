'use client'; 

// Importing the tools I need from React and the Swiper carousel library.
import React, { useState, useRef } from 'react';
import { Swiper, SwiperSlide } from 'swiper/react';
import { EffectCoverflow, Pagination, Autoplay } from 'swiper/modules';
import type { Swiper as SwiperCore } from 'swiper';
import 'swiper/css';
import 'swiper/css/effect-coverflow';
import 'swiper/css/pagination';
import { callAgentAPI } from "@/services/apiClient";
import Image from 'next/image';

export default function Home() {
  // Here, I'm setting up the state for my component. This is the information
  // that will change as the user interacts with the page.
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [currentUserQuery, setCurrentUserQuery] = useState('');
  const [currentAgentReply, setCurrentAgentReply] = useState('');
  const [highlightedMemoryId, setHighlightedMemoryId] = useState<number | null>(null);
  const [agentReply, setAgentReply] = useState<string>("");

  // This ref gives me direct control over the carousel component.
  const carouselRef = useRef<SwiperCore | null>(null);

  // This is the hard-coded conversation I'm using for the demo.
  const demoConversation = [
    {
      query: "Who was that person I met at TechCrunch who worked on crypto payments?",
      response: "That would be Jennifer Chen, VP of Engineering at Stripe! You met her at their booth on day 2 of TechCrunch conference. She mentioned they were hiring senior engineers for their crypto payments team."
    },
    {
      query: "Right! What else did we talk about?",
      response: "You both bonded over being Stanford alumni, and she specifically mentioned their new payment APIs. You took a photo together at their booth, and she gave you her business card with instructions to reach out about the senior engineering role."
    },
    {
      query: "Did I ever follow up with her?",
      response: "Yes, I reminded you on Tuesday morning as requested, and you sent her a LinkedIn message that same day. She responded within 2 hours suggesting a coffee meeting, which you scheduled for the next Friday. You met at Blue Bottle Coffee downtown and had what you described as a 'great conversation about team culture and technical challenges.'"
    },
    {
      query: "Perfect. I'm interviewing at Coinbase tomorrow and want to mention my connection to Stripe's crypto work. Can you give me some talking points?",
      response: "Based on your conversation with Jennifer, here are some relevant points: • Stripe is actively investing in crypto infrastructure with dedicated teams • They're focusing on enterprise-grade payment solutions (Jennifer's emphasis) • Their approach prioritizes regulatory compliance and security • Jennifer mentioned they're seeing huge demand from fintech companies. This shows you're plugged into industry trends and have insights from a senior leader in the space. Would you like me to find other crypto-related conversations from your memory?"
    }
  ];

  // This is the list of photos for the carousel.
  const memoryPhotos = [
    { id: 1, name: 'Jennifer Chen', imageUrl: '/placeholder.png' },
    { id: 2, name: 'Jake\'s Bday', imageUrl: '/placeholder.png' },
    { id: 3, name: 'Coffee Meetup', imageUrl: '/placeholder.png' },
    { id: 4, name: 'Team Lunch', imageUrl: '/placeholder.png' },
    { id: 5, name: 'Project Demo', imageUrl: '/placeholder.png' },
  ];

  // This function runs when the microphone button is clicked.
  const runNextStepInDemo = () => {
    const jenniferId = 1;
    const jenniferIndex = memoryPhotos.findIndex(m => m.id === jenniferId);

    // On the first click of the demo, I'll stop the autoplay and slide to Jennifer's photo.
    if (currentStepIndex === 0) {
      setHighlightedMemoryId(jenniferId);
      if (carouselRef.current && jenniferIndex !== -1) {
        carouselRef.current.autoplay.stop();
        carouselRef.current.slideToLoop(jenniferIndex);
      }
    }

    // I'll display the current step of the conversation...
    const currentStep = demoConversation[currentStepIndex];
    setCurrentUserQuery(currentStep.query);
    setCurrentAgentReply(currentStep.response);
    
    // ...and then get ready for the next click by advancing the step index.
    setCurrentStepIndex((prevIndex) => (prevIndex + 1) % demoConversation.length);
  };

  const handleAskAgent = async (query: string) => {
    const result = await callAgentAPI(query);
    setAgentReply(result.response || JSON.stringify(result));
  };

  return (
    <div className="bg-gray-900 text-gray-100 min-h-screen flex flex-col font-sans p-5 sm:p-8 overflow-y-auto">
      
      <header className="flex justify-between items-center pb-5 border-b border-gray-700 flex-shrink-0">
        <div className="text-2xl font-bold">Live Witness</div>
        <nav className="flex gap-4 sm:gap-6 text-gray-400">
          <a href="/our-project" className="hover:text-white transition-colors">Our Project</a>
          <a href="/meet-your-agents" className="hover:text-white transition-colors">Meet Your Agents</a>
          <a href="/settings" className="hover:text-white transition-colors">Settings</a>
        </nav>
      </header>
      
      <main className="flex-grow flex flex-col items-center justify-start pt-10 w-full space-y-8">
        
        <Swiper
          onSwiper={(swiper) => { carouselRef.current = swiper; }}
          effect={'coverflow'}
          grabCursor={true}
          centeredSlides={true}
          slidesPerView={3}
          loop={true}
          autoplay={{ delay: 3000, disableOnInteraction: false }}
          coverflowEffect={{ rotate: 0, stretch: 0, depth: 150, modifier: 1, slideShadows: false }}
          pagination={false}
          modules={[EffectCoverflow, Pagination, Autoplay]}
          className="w-full max-w-5xl"
        >
          {memoryPhotos.map(photo => (
            <SwiperSlide key={photo.id}>
              <div className="flex flex-col items-center justify-center h-full pt-10">
                <Image 
                  src={photo.imageUrl} 
                  alt={photo.name || ''}
                  width={160} height={160}
                  className={`w-32 h-32 sm:w-40 sm:h-40 object-cover rounded-xl border-2 transition-all duration-300 ${
                    highlightedMemoryId === photo.id 
                    ? 'border-blue-400 scale-110'
                    : 'border-gray-600'
                  }`}
                />
                <span className="block mt-2 text-sm">{photo.name}</span>
              </div>
            </SwiperSlide>
          ))}
        </Swiper>
       
        <div className="flex justify-center items-center gap-12 w-full">
          <div className="flex items-center gap-4">
            <button 
              onClick={runNextStepInDemo}
              className="bg-gray-800 hover:bg-gray-700 transition-colors border border-gray-600 rounded-full w-16 h-16 text-4xl flex items-center justify-center flex-shrink-0"
            >
              🎤
            </button>
            <p className="text-gray-400 italic text-lg">&quot;{currentUserQuery || 'Click the mic to start the conversation...'}&quot;</p>
          </div>
          <button className="bg-gray-800 hover:bg-gray-700 transition-colors border border-gray-600 rounded-full w-16 h-16 text-4xl flex items-center justify-center flex-shrink-0">
            🖼️
          </button>
        </div>
        
        {currentAgentReply && (
            <div className="mt-4 bg-gray-800 p-6 rounded-lg w-full max-w-3xl border border-gray-700">
                <strong className="text-blue-400">AI Response:</strong>
                <p className="mt-2 whitespace-pre-line">{currentAgentReply}</p>
            </div>
        )}
        <div>
          <button onClick={() => handleAskAgent("calculate 2 + 2")}>Ask Agent</button>
          {agentReply && <div>{agentReply}</div>}
        </div>
      </main>
    </div>
  );
}