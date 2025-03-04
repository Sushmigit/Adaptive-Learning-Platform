import React from "react";
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

export default ModuleSelection;
