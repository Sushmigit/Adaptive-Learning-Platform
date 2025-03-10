from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
from flask_cors import CORS
import os
import joblib
import numpy as np
import tensorflow as tf
import xgboost as xgb
from tensorflow.keras.models import load_model
from tensorflow.keras.models import Model

app = Flask(__name__)
CORS(app)  # Enable CORS globally

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123Sushmi@123",
        database="letter_sound_db"
    )

@app.route('/')
def home():
    return "Flask API is running! Use /get_sounds to fetch data."

# Serve audio files
@app.route('/audio/<filename>')
def serve_audio(filename):
    audio_folder = os.path.join(app.root_path, 'static/sounds')
    return send_from_directory(audio_folder, filename, mimetype="audio/mpeg")

# Fetch letter sounds from MySQL
@app.route('/get_sounds', methods=['GET'])
def get_sounds():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT letter, audio_path FROM sounds")
    sounds = cursor.fetchall()
    conn.close()
    
    for sound in sounds:
        filename = os.path.basename(sound['audio_path'])
        sound["audio_path"] = f"http://127.0.0.1:5000/audio/{filename}"
    
    return jsonify(sounds)
@app.route('/get_word_sounds', methods=['GET'])
def get_word_sounds():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT word, audio_path FROM word_sounds")  # Assuming table name is 'word_sounds'
    word_sounds = cursor.fetchall()
    conn.close()
    
    for word in word_sounds:
        filename = os.path.basename(word['audio_path'])
        word["audio_path"] = f"http://127.0.0.1:5000/audio/{filename}"
    
    return jsonify(word_sounds)

# User Registration
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO reg (child_name, age, grade, parent_name, email_id, mobile_no, username, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['child_name'], data['age'], data['grade'], data['parent_name'],
              data['email_id'], data['mobile_no'], data['username'], data['password']))

        learner_id = cursor.lastrowid
        cursor.execute("""
            INSERT INTO letter_sound_login (learner_id, username, password, session_id, difficulty_level)
            VALUES (%s, %s, %s, 0, 'easy1')
        """, (learner_id, data['username'], data['password']))
        cursor.execute("""
            INSERT INTO word_sound_login (learner_id, username, password, session_id, difficulty_level)
            VALUES (%s, %s, %s, 0, 'easy1')
        """, (learner_id, data['username'], data['password']))
        conn.commit()
        return jsonify({"message": "Registration successful", "learner_id": learner_id})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

# User Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT learner_id, username, difficulty_level, session_id FROM letter_sound_login
            WHERE username = %s AND password = %s
        """, (data['username'], data['password']))

        user = cursor.fetchone()
        if user:
            return jsonify({
                "message": "Login successful",
                "learner_id": user['learner_id'],
                "username": user['username'],
                "difficulty_level": user['difficulty_level'],
                "session_id": user['session_id']
            })
        else:
            return jsonify({"message": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

# Get User Details
@app.route('/get_user_details/<username>', methods=['GET'])
def get_user_details(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT learner_id, session_id, difficulty_level FROM letter_sound_login WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            print("User Details Retrieved:", user)  # Debugging Log
            return jsonify(user)
        else:
            print("User not found for username:", username)  # Debugging Log
            return jsonify({"message": "User not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()


# Predict next difficulty level

def predict_next_difficulty(current_difficulty, accuracy, error_rate, response_time):  
    try:
        # Load saved models
        lstm_model = load_model("model/lstm_model.h5")
        xgb_model = joblib.load("model/xgb_model.pkl")
        scaler = joblib.load("model/scaler.pkl")

        difficulty_levels = ["easy1", "easy2", "easy3", "medium1", "medium2", "medium3", "hard1", "hard2", "hard3"]
        inverse_difficulty_encoder = {i: level for i, level in enumerate(difficulty_levels)}

# Create a sample input (random values within normalized range)
        sample_input = np.array([[accuracy, error_rate, response_time, difficulty_levels.index(current_difficulty)]])   # Example: accuracy=0.8, error_rate=0.2, response_time=0.5, difficulty="Easy 3"

# Normalize input using the saved scaler
        sample_input_scaled = scaler.transform(sample_input)

# Reshape for LSTM model
        sample_input_lstm = sample_input_scaled.reshape(1, 1, sample_input.shape[1])

# Predict features using LSTM
        lstm_features = lstm_model.predict(sample_input_lstm).reshape(1, -1)

# Predict difficulty level using XGBoost
        predicted_label = xgb_model.predict(lstm_features)[0]

# Convert numerical prediction to difficulty level    
        predicted_difficulty = inverse_difficulty_encoder[predicted_label]

        print(f"Predicted Next Difficulty Level: {predicted_difficulty}")
    except:
        print("error")    
# Store Performance Metrics
@app.route('/store_metrics', methods=['POST'])
@app.route('/store_metrics', methods=['POST'])
def store_metrics():
    data = request.json
    print("Received data:", data)  # Debugging Log

    required_fields = ['learner_id', 'session_id', 'module_name', 'difficulty_level', 'accuracy', 'error_rate', 'response_time', 'task_completion_rate']
    for field in required_fields:
        if field not in data or data[field] is None:
            return jsonify({"error": f"Missing or null field: {field}"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Step 1: Insert the current session's metrics into the database
        cursor.execute("""
            INSERT INTO performance_metrics (learner_id, session_id, module_name, difficulty_level, accuracy, error_rate, response_time, task_completion_rate)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['learner_id'], data['session_id'], data['module_name'], data['difficulty_level'],
            data['accuracy'], data['error_rate'], data['response_time'], data['task_completion_rate']
        ))
        conn.commit()

        

        # Step 3: Predict the next difficulty level
        predicted_difficulty = predict_next_difficulty(
            current_difficulty=data['difficulty_level'],
            accuracy=data['accuracy'],
            error_rate=data['error_rate'],
            response_time=data['response_time'],
        )
        
        # Print prediction in console (as requested)
        print(f"Predicted Next Difficulty Level: {predicted_difficulty}")
        print(label_encoder.classes_)  
        
        return jsonify({
            "message": "Metrics stored successfully!",
            "next_difficulty": predicted_difficulty
        })

    except Exception as e:
        print("Error in /store_metrics:", str(e))  # Debugging Log
        return jsonify({"error": str(e)}), 500

    finally:
        conn.close()

# Run Flask App
if __name__ == '__main__':
    app.run(debug=True)
