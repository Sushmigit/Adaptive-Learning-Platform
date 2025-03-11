from gtts import gTTS  

# List of three-letter words  
words = ["cat", "dog", "bat"]  

# Generate and save audio files  
for word in words:  
    tts = gTTS(word, lang='en')  
    tts.save(f"{word}.mp3")  

print("Audio files saved!")  
