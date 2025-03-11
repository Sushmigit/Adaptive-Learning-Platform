import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import "../styles/Assessment1.css";

const questions = [
  { id: 1, audioPath: "http://127.0.0.1:5000/audio/w1.mp3", correctAnswer: "bat", options: ["bat", "cat", "dog"] },
  { id: 2, audioPath: "http://127.0.0.1:5000/audio/w2.mp3", correctAnswer: "cat", options:  ["bat", "cat", "dog"] },
  { id: 3, audioPath: "http://127.0.0.1:5000/audio/w3.mp3", correctAnswer: "dog", options: ["bat", "cat", "dog"] },
];

const Assessment2 = () => {
  const location = useLocation();
  const params = new URLSearchParams(location.search);

  const learnerId = params.get("learner_id");
  const username = params.get("username");
  const difficultyLevel = params.get("difficulty_level");
  const sessionId = params.get("session_id");
  const moduleName = params.get("module");

  console.log("Extracted Data:", { learnerId, username, difficultyLevel, sessionId, moduleName });

  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [startTime, setStartTime] = useState(Date.now());
  const [responseTime, setResponseTime] = useState(0);

  const handleAnswerSelect = (questionId, answer) => {
    setSelectedAnswers({ ...selectedAnswers, [questionId]: answer });
  };

  const checkAnswers = async () => {
    setShowResults(true);
    const endTime = Date.now();
    const timeTaken = (endTime - startTime) / 1000; // Convert to seconds
    setResponseTime(timeTaken);

    const totalQuestions = questions.length;
    const answeredQuestions = Object.keys(selectedAnswers).length;
    const correctAnswers = questions.filter(q => selectedAnswers[q.id] === q.correctAnswer).length;
    
    const accuracy = (correctAnswers / totalQuestions) * 100;
    const errorRate = 100 - accuracy;
    const taskCompletionRate = answeredQuestions / totalQuestions; // Now between 0 and 1
    
    const metricsData = {
      learner_id: learnerId,
      session_id: sessionId,
      module_name: moduleName,
      difficulty_level: difficultyLevel,
      accuracy: accuracy.toFixed(2),
      error_rate: errorRate.toFixed(2),
      response_time: timeTaken.toFixed(2),
      task_completion_rate: taskCompletionRate.toFixed(2),
    };

    console.log("Sending Metrics:", metricsData);

    await fetch("http://127.0.0.1:5000/store_metrics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(metricsData),
    });
  };

  const backgroundStyle = {
    backgroundImage: `url(${process.env.PUBLIC_URL}/images/jungle.jpg)`,
    backgroundSize: "cover",
    backgroundPosition: "center",
    height: "100vh",
  };

  return (
    <div className="jungle-assessment-container" style={backgroundStyle}>
      <h2 className="jungle-heading">Assessment</h2>
      {questions.map((question) => (
        <div key={question.id} className="jungle-question-container">
          <button className="jungle-audio-button" onClick={() => new Audio(question.audioPath).play()}>
            Play Sound
          </button>
          <div className="jungle-options-container">
            {question.options.map((option) => {
              const isCorrect = showResults && option === question.correctAnswer;
              const isIncorrect =
                showResults && selectedAnswers[question.id] === option && option !== question.correctAnswer;
              const isSelected = selectedAnswers[question.id] === option;

              return (
                <button
                  key={option}
                  onClick={() => handleAnswerSelect(question.id, option)}
                  className={`jungle-option-button 
                    ${isCorrect ? "correct" : ""}
                    ${isIncorrect ? "incorrect" : ""}
                    ${isSelected ? "selected" : ""}
                  `}
                >
                  {option}
                </button>
              );
            })}
          </div>

          {showResults && selectedAnswers[question.id] !== question.correctAnswer && (
            <p className="jungle-correct-answer">
              ❌ Incorrect! The correct answer is: <strong>{question.correctAnswer}</strong>
            </p>
          )}

          {showResults && selectedAnswers[question.id] === question.correctAnswer && (
            <p className="jungle-correct-answer">✅ Correct!</p>
          )}
        </div>
      ))}
      <button onClick={checkAnswers} className="jungle-submit-button">
        Submit Answers
      </button>
    </div>
  );
};

export default Assessment2;
