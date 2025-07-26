import React, { useState, useRef, useEffect } from "react";

export default function ChatBot({ user, onLogout }) {
  const [messages, setMessages] = useState([
    {
      sender: "ai",
      text: "Hello! I am Kiran, your White Mirror AI. How are you feeling today, or what do you want to explore?"
    }
  ]);
  const [input, setInput] = useState("");
  const bottomRef = useRef();

  // Scroll to the newest message
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  async function sendToServer(message) {
    // You may need to use http://127.0.0.1:8000 if localhost doesn't work
    const res = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, user: user?.email })
    });
    if (!res.ok) throw new Error("Server error");
    const data = await res.json();
    return data.reply || "Sorry, I couldn't process that.";
  }
  
  function handleSend(e) {
    e.preventDefault();
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
  
    // 🔥 Use your backend now!
    sendToServer(input)
      .then(aiReply => {
        setMessages(prev => [
          ...prev,
          { sender: "ai", text: aiReply }
        ]);
      })
      .catch(() => {
        setMessages(prev => [
          ...prev,
          { sender: "ai", text: "There was an error reaching the AI server." }
        ]);
      });
  }
  

  return (
    <div style={{
      width: "100%",
      minHeight: 800,
      maxWidth: 800,
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      background: "rgba(30, 38, 64, 0.90)",
      borderRadius: 22,
      boxShadow: "0 8px 44px #37a0ff28",
      padding: "22px 16px"
    }}>
      <div style={{
        width: "100%",
        textAlign: "center",
        fontSize: 22,
        color: "#aee7ff",
        fontWeight: 700,
        marginBottom: 8,
        letterSpacing: 1.2
      }}>
        Hi, {user?.email?.split("@")[0] || "User"}!
      </div>
      <div style={{
        width: "100%",
        flex: 1,
        overflowY: "auto",
        maxHeight: 700,
        marginBottom: 10,
        background: "rgba(19,25,44,0.7)",
        borderRadius: 12,
        padding: "11px 12px"
      }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              textAlign: msg.sender === "user" ? "right" : "left",
              margin: "10px 0"
            }}
          >
            <span
              style={{
                display: "inline-block",
                padding: "9px 15px",
                borderRadius: 14,
                background:
                  msg.sender === "user"
                    ? "linear-gradient(90deg, #1a50a5 60%, #208bdb 100%)"
                    : "linear-gradient(90deg, #162044 75%, #36e0ff 120%)",
                color: "#eafaff",
                fontWeight: 500,
                maxWidth: 500,
                fontSize: 15,
                wordBreak: "break-word",
                boxShadow:
                  msg.sender === "user"
                    ? "0 2px 8px #36e0ff33"
                    : "0 1.5px 8px #2977f533"
              }}
            >
              {msg.text}
            </span>
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <form
        onSubmit={handleSend}
        style={{ width: "100%", display: "flex", alignItems: "center" }}
      >
        <input
          type="text"
          value={input}
          placeholder="Type your thoughts…"
          onChange={e => setInput(e.target.value)}
          style={{
            flex: 1,
            padding: "12px 13px",
            borderRadius: 13,
            border: "1.5px solid #28395b",
            background: "#1a2135",
            color: "#b7e4ff",
            fontSize: 15,
            marginRight: 9
          }}
          autoFocus
        />
        <button
          type="submit"
          style={{
            padding: "12px 24px",
            borderRadius: 13,
            background: "linear-gradient(90deg, #269fff 40%, #00ebff 100%)",
            color: "#111829",
            fontWeight: 800,
            fontSize: 16,
            border: "none",
            cursor: "pointer",
            boxShadow: "0 2px 18px #2a90e630"
          }}
        >
          Send
        </button>
      </form>
    </div>
  );
}
