// src/components/Register.jsx
import React, { useState } from "react";

export default function Register({ onRegister }) {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    onRegister({ email, username, password });
  }

  return (
    <div className="auth-container">
      <h2 style={{ marginBottom: 12 }}>Register for White Mirror</h2>
      <form onSubmit={handleSubmit} className="auth-form" style={{ width: "100%" }}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        <button className="white-blue-btn" type="submit">Register</button>
      </form>
    </div>
  );
}
