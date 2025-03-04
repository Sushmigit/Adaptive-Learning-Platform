import React, { useState } from "react";
import "../styles/Register.css";

const Register = () => {
  const [formData, setFormData] = useState({
    child_name: "",
    age: "",
    grade: "",
    parent_name: "",
    email_id: "",
    mobile_no: "",
    username: "",  // Added username field
    password: "",
  });

  const [message, setMessage] = useState("");
  const [learnerId, setLearnerId] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch("http://127.0.0.1:5000/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData),
    });

    const data = await response.json();
    setMessage(data.message);
    if (data.learner_id) {
      setLearnerId(data.learner_id);
    }
  };

  return (
    <div className="register-container">
      <h2>Register</h2>
      <form onSubmit={handleSubmit}>
        <input type="text" name="child_name" placeholder="Child's Name" onChange={handleChange} required />
        <input type="number" name="age" placeholder="Age" onChange={handleChange} required />
        <input type="text" name="grade" placeholder="Grade" onChange={handleChange} required />
        <input type="text" name="parent_name" placeholder="Parent Name" onChange={handleChange} required />
        <input type="email" name="email_id" placeholder="Email ID" onChange={handleChange} required />
        <input type="tel" name="mobile_no" placeholder="Mobile Number" onChange={handleChange} required />
        <input type="text" name="username" placeholder="Username" onChange={handleChange} required />  {/* Added username field */}
        <input type="password" name="password" placeholder="Password" onChange={handleChange} required />
        <button type="submit">Register</button>
      </form>
      {message && <p>{message}</p>}
      {learnerId && <p>Your Learner ID: <strong>{learnerId}</strong></p>}
    </div>
  );
};

export default Register;
