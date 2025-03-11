import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import LetterButton from "./LetterButton";
import AudioPlayer from "./AudioPlayer";
import "../styles/LetterSoundGame1.css";

const API_URL = "http://127.0.0.1:5000/get_word_sounds";

const WordSoundGame = () => {
  const [letters, setLetters] = useState([]);
  const [currentAudio, setCurrentAudio] = useState(null);
  const location = useLocation();
  const navigate = useNavigate();

  // Extract parameters from URL
  const params = new URLSearchParams(location.search);
  const learner_id = params.get("learner_id");
  const username = params.get("username");
  const difficulty_level = params.get("difficulty_level");
  const session_id = params.get("session_id");
  const module = params.get("module");

  useEffect(() => {
    fetch(API_URL)
      .then((res) => res.json())
      .then((data) => setLetters(data))
      .catch((err) => console.error("Error fetching sounds:", err));
  }, []);

  const handlePlaySound = (letter) => {
    const audioData = letters.find((item) => item.letter === letter);
    if (audioData) {
      setCurrentAudio(audioData.audio_path);
    }
  };

  const backgroundStyle = {
    backgroundImage: `url(${process.env.PUBLIC_URL}/images/jungle.jpg)`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    height: "100vh",
  };

  return (
    <div className="jungle-container" style={backgroundStyle}>
      <div className="sidebar">
        <h3 className="sidebar-heading">Menu</h3>
        <ul className="sidebar-list">
          <li className="sidebar-item"><Link to="/" className="link">Home</Link></li>
          <li className="sidebar-item">
            <button
              className="link-button"
              onClick={() => navigate(`/assessment2?learner_id=${learner_id}&username=${username}&difficulty_level=${difficulty_level}&session_id=${session_id}&module=${module}`)}
            >
              Assessment
            </button>
          </li>
          <li className="sidebar-item">Settings</li>
        </ul>
      </div>

      <div className="jungle-content">
        <h1 className="main-heading">Letter Sound Recognition</h1>
        <h2>Tap a letter to hear its sound</h2>
        <div className="letter-grid">
          {letters.map((item) => (
            <LetterButton
              key={item.letter}
              letter={item.letter}
              onClick={handlePlaySound}
              className="letter-button"
            />
          ))}
        </div>
        {currentAudio && <AudioPlayer audioSrc={currentAudio} />}
      </div>
    </div>
  );
};

export default WordSoundGame;
