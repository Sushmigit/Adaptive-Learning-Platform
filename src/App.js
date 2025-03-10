import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LetterSoundGame from "./components/LetterSoundGame";

import Assessment from "./components/Assessment";
import Register from "./components/Register";
import Login from "./components/Login";
import ModuleSelection from "./components/ModuleSelection";


function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/modules" element={<ModuleSelection />} />
          <Route path="/assessment" element={<Assessment />} />
          <Route path="/LetterSoundGame" element={<LetterSoundGame />} />
          
        </Routes>
      </div>
    </Router>
  );
}

export default App;
