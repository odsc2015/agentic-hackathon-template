// src/components/Login.jsx
import React, { useState } from "react";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    onLogin({ email, password });
  }

  return (
    <div className="auth-container">
      <h2 style={{ marginBottom: 12, color: '#fff' }}>Login to White Mirror</h2>
      <form onSubmit={handleSubmit} className="auth-form" style={{ width: "100%" }}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button className="white-blue-btn" type="submit">Login</button>
      </form>
    </div>
  );
}
