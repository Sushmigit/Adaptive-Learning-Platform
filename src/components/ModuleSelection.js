/*import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/ModuleSelection.css";

const modules = [
  "Phoneme Blending",
  "Rhyming Words",
  "Syllable Splitting",
  "Sentence Formation",
  "Letter Sound Recognition",
  "Listening and Identifying Sounds",
];

const ModuleSelection = () => {
  const navigate = useNavigate();

  // Retrieve stored user data
  const learner_id = localStorage.getItem("learner_id");
  const username = localStorage.getItem("username");
  const difficulty_level = localStorage.getItem("difficulty_level");
  const session_id = localStorage.getItem("session_id");

  const handleModuleSelect = (module) => {
    const moduleName = module.replace(/\s+/g, "-").toLowerCase(); // Convert to URL-friendly format

    navigate(`/LetterSoundGame?learner_id=${learner_id}&username=${username}&difficulty_level=${difficulty_level}&session_id=${session_id}&module=${moduleName}`);
  };

  return (
    <div className="module-selection-container">
      <h2>Select a Module</h2>
      <p>Welcome, {username}!</p>
      <div className="module-list">
        {modules.map((module) => (
          <button key={module} className="module-button" onClick={() => handleModuleSelect(module)}>
            {module}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ModuleSelection;*/
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/ModuleSelection.css";
const modules = [
  "Phoneme Blending",
  "Rhyming Words",
  "Syllable Splitting",
  "Sentence Formation",
  "Letter Sound Recognition",
  "Listening and Identifying Sounds",
];

const ModuleSelection = () => {
  const navigate = useNavigate();
  const learner_id = localStorage.getItem("learner_id");
  const username = localStorage.getItem("username");

  const [error, setError] = useState("");

  const fetchSessionAndDifficulty = async (tableName) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/get_user_details/${username}?table=${tableName}`);
      const data = await response.json();

      if (response.ok) {
        return { session_id: data.session_id, difficulty_level: data.difficulty_level };
      } else {
        throw new Error(data.message || "Error fetching user details");
      }
    } catch (error) {
      setError(error.message);
      return { session_id: "0", difficulty_level: "easy1" }; // Default fallback
    }
  };

  const handleModuleSelect = async (module) => {
    const moduleName = module.replace(/\s+/g, "-").toLowerCase();

    let tableName = "";
    let gamePage = "/LetterSoundGame"; // Default game page

    if (module === "Letter Sound Recognition") {
      tableName = "letter_sound_login";
    } else if (module === "Listening and Identifying Sounds") {
      tableName = "word_sound_login";
      gamePage = "/WordSoundGame"; // Change navigation path for this module
    }

    let session_id = "0";
    let difficulty_level = "easy1";

    if (tableName) {
      const data = await fetchSessionAndDifficulty(tableName);
      session_id = data.session_id;
      difficulty_level = data.difficulty_level;
    } else {
      session_id = localStorage.getItem("session_id");
      difficulty_level = localStorage.getItem("difficulty_level");
    }

    navigate(
      `${gamePage}?learner_id=${learner_id}&username=${username}&difficulty_level=${difficulty_level}&session_id=${session_id}&module=${moduleName}`
    );
  };

  return (
    <div className="module-selection-container">
      <h2>Select a Module</h2>
      <p>Welcome, {username}!</p>
      {error && <p className="error">{error}</p>}
      <div className="module-list">
        {modules.map((module) => (
          <button key={module} className="module-button" onClick={() => handleModuleSelect(module)}>
            {module}
          </button>
        ))}
      </div>
    </div>
  );
};

export default ModuleSelection;

