import React, { useState } from "react";
import "../styles/LetterButton.css"; // Ensure the CSS file is imported

const LetterButton = ({ letter, onClick }) => {
  const [isActive, setIsActive] = useState(false);

  const handleClick = () => {
    setIsActive(true);
    onClick(letter);

    // Reset animation after 500ms
    setTimeout(() => setIsActive(false), 500);
  };

  return (
    <button
      className={`letter-button ${isActive ? "active" : ""}`}
      onClick={handleClick}
    >
      {letter}
    </button>
  );
};

export default LetterButton;
