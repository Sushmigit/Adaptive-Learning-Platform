// src/components/AudioPlayer.js
import React, { useEffect, useRef } from "react";

const AudioPlayer = ({ audioSrc }) => {
  const audioRef = useRef(null);

  useEffect(() => {
    if (audioSrc) {
      audioRef.current.play();
    }
  }, [audioSrc]);

  return <audio ref={audioRef} src={audioSrc} />;
};

export default AudioPlayer;
