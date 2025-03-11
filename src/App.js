import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LetterSoundGame from "./components/LetterSoundGame";

import Assessment from "./components/Assessment";
import Assessment2 from "./components/Assessment2";
import Register from "./components/Register";
import Login from "./components/Login";
import ModuleSelection from "./components/ModuleSelection";
import WordSoundGame from "./components/WordSoundGame";


function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/modules" element={<ModuleSelection />} />
          <Route path="/assessment" element={<Assessment />} />
          <Route path="/assessment2" element={<Assessment2 />} />
          <Route path="/LetterSoundGame" element={<LetterSoundGame />} />
          <Route path="/WordSoundGame" element={<WordSoundGame />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
