import React, { useEffect } from "react";

const introText = "Welcome to White Mirror. Your personal cognitive companion, where neuroscience meets the future. Let's begin your journey.";

export default function VoiceIntro({ trigger = "auto" }) {
  // "auto" = play on mount, "button" = user must click
  useEffect(() => {
    if (trigger !== "auto") return;
    // Prevent double play if user leaves and returns quickly
    if (window.voiceIntroPlayed) return;
    window.voiceIntroPlayed = true;
    const utter = new window.SpeechSynthesisUtterance(introText);
    utter.lang = "en-US";
    utter.pitch = 1.1;
    utter.rate = 1;
    utter.volume = 1;
    // Try to pick a female US voice, fallback to default
    const voice = window.speechSynthesis.getVoices().find(
      v => v.lang === "en-US" && v.name.toLowerCase().includes("female")
    );
    if (voice) utter.voice = voice;
    setTimeout(() => window.speechSynthesis.speak(utter), 350);
    // Cleanup: cancel speech if component unmounts
    return () => window.speechSynthesis.cancel();
  }, [trigger]);

  // For button-triggered speech
  function handleClick() {
    const utter = new window.SpeechSynthesisUtterance(introText);
    utter.lang = "en-US";
    utter.pitch = 1.1;
    utter.rate = 1;
    utter.volume = 1;
    window.speechSynthesis.speak(utter);
  }

  if (trigger === "button") {
    return (
      <button
        onClick={handleClick}
        style={{
          marginBottom: 20,
          background: "#18253a",
          color: "#7fd4ff",
          border: "1.5px solid #274476",
          borderRadius: 9,
          fontWeight: 700,
          fontSize: 16,
          boxShadow: "0 4px 16px 0 #70b4ff22",
          cursor: "pointer",
          outline: "none",
          padding: "10px 18px"
        }}
      >
        🔊 Hear Introduction
      </button>
    );
  }

  return null;
}
