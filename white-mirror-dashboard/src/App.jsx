import React, { useState } from "react";
import Login from "/components/Login";
import Register from "/components/Register";
import DigitalBrain from "/components/DigitalBrain";
import VoiceIntro from "/components/VoiceIntro";
import ChatBot from "/components/ChatBot";

export default function App() {
  const [page, setPage] = useState("login");
  const [user, setUser] = useState(null);

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(circle at 65% 20%, #162044 40%, #0b0e16 100%)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Header */}
      <header
        style={{
          height: 72,
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 44px",
          background: "rgba(10,12,26,0.94)",
          borderBottom: "1.5px solid #283376",
          backdropFilter: "blur(8px)",
        }}
      >
        <div
          style={{
            fontSize: 29,
            fontWeight: 800,
            color: "#73c7ff",
            letterSpacing: 1.5,
            textShadow: "0 2px 22px #2988ee80",
          }}
        >
          <span role="img" aria-label="White Mirror">
            🧠
          </span>{" "}
          White Mirror
          <VoiceIntro trigger="auto" />
        </div>
        <nav>
          <button className="nav-btn-dark" onClick={() => setPage("about")}>
            About
          </button>
          <button className="nav-btn-dark" onClick={() => setPage("contact")}>
            Contact Us
          </button>
          {!user && (
            <>
              <button className="nav-btn-dark" onClick={() => setPage("login")}>
                Login
              </button>
              <button
                className="nav-btn-dark"
                onClick={() => setPage("register")}
              >
                Register
              </button>
            </>
          )}
        </nav>
      </header>

      {/* Main Split Panel */}
      <main
        style={{
          flex: 1,
          display: "flex",
          minHeight: 0,
          width: "100%",
          height: "calc(100vh - 72px)",
        }}
      >
        {/* Left Panel */}
        <div
          style={{
            width: "25%",
            minWidth: 320,
            maxWidth: 500,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "rgba(23,28,44,0.95)",
            borderRight: "1.5px solid #29407a",
            boxShadow: "8px 0 70px 0 #2977f555",
            backdropFilter: "blur(8px)",
          }}
        >
          <div
            style={{
              width: "92%",
              borderRadius: 28,
              background: "rgba(19,22,38,0.97)",
              padding: "46px 22px",
              boxShadow: "0 6px 44px 0 #2988ee22",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
          >
            {page === "login" && (
              <Login
                onLogin={() => {
                  setUser({ email: "alice@example.com" });
                  setPage("chatbot");
                }}
              />
            )}
            {page === "register" && (
              <Register
                onRegister={() => {
                  setUser({ email: "test" });
                  setPage("chatbot");
                }}
              />
            )}
            {page === "about" && (
              <div style={{ textAlign: "center", color: "#85b9ff" }}>
                <h2>About White Mirror</h2>
                <p>
                  White Mirror is your digital cognitive companion, blending
                  neuroscience and AI.
                  <br />
                  Discover new ways to reflect, learn, and grow with our
                  personalized, private tools.
                </p>
              </div>
            )}
            {page === "contact" && (
              <div style={{ textAlign: "center", color: "#85b9ff" }}>
                <h2>Contact Us</h2>
                <p>
                  hello@whitemirror.app
                  <br />
                  &copy; {new Date().getFullYear()} White Mirror
                </p>
              </div>
            )}
            {page === "chatbot" && user && (
              <div style={{ textAlign: "center", color: "#85b9ff" }}>
                <h2>Welcome, {user.email}!</h2>
                {/* Place your chatbot component here */}
                <DigitalBrain />
              </div>
            )}
          </div>
        </div>
        {/* Right Panel */}
        <div
          style={{
            flex: 1,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            background: "linear-gradient(120deg, #171c2c 55%, #0b0e16 100%)",
          }}
        >
         
            {page === "chatbot" && user ? (
              <ChatBot
                user={user}
                onLogout={() => {
                  setUser(null);
                  setPage("login");
                }}
              />
            ) : (
              <div
              style={{
                width: 470,
                height: 470,
                background:
                  "radial-gradient(ellipse at 70% 20%, #183b59 65%, #102041 100%)",
                borderRadius: "50%",
                boxShadow: "0 0 120px 20px #37a0ff60, 0 8px 50px #2977f530",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                backdropFilter: "blur(8px)",
              }}
            >
              <DigitalBrain />
              </div>
            )}
        
        </div>
      </main>
    </div>
  );
}
