import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/Login.css";

const Login = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  /*const handleLogin = async (e) => {
    e.preventDefault();
    setError("");

    const response = await fetch("http://127.0.0.1:5000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });

    const data = await response.json();

    if (response.ok) {
      // Store user details in localStorage
      localStorage.setItem("learner_id", data.learner_id);
      localStorage.setItem("username", data.username);
      localStorage.setItem("difficulty_level", data.difficulty_level);
      localStorage.setItem("session_id", data.session_id);

      // Navigate to the module selection page
      navigate("/modules");
    } else {
      setError(data.message);
    }
  };*/
  const handleLogin = async (e) => {
    e.preventDefault();
    setError("");
  
    const response = await fetch("http://127.0.0.1:5000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password }),
    });
  
    const data = await response.json();
  
    if (response.ok) {
      // Navigate to the module selection page with state
      navigate("/modules", { state: { username: data.username, learner_id: data.learner_id } });
    } else {
      setError(data.message);
    }
  };
  

  return (
    <div className="login-container">
      <h2>Login</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleLogin}>
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit">Login</button>
      </form>
    </div>
  );
};

export default Login;
