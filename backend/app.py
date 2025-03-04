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

def predict_next_difficulty(learner_id, session_id, current_difficulty, accuracy, error_rate, response_time, task_completion_rate, 
                            avg_accuracy, avg_error_rate, avg_response_time, avg_task_completion_rate):  
    try:
        # Load saved models
        lstm_model = load_model("model/lstm_model.h5")
        xgb_model = joblib.load("model/xgb_model.pkl")
        scaler = joblib.load("model/scaler.pkl")

        # Define difficulty levels
        difficulty_order = ["Easy 1", "Easy 2", "Easy 3", "Medium 1", "Medium 2", "Medium 3", "Hard 1", "Hard 2", "Hard 3"]
        difficulty_map = {level: idx for idx, level in enumerate(difficulty_order)}

        # Ensure current difficulty is mapped correctly
        if current_difficulty not in difficulty_map:
            raise ValueError(f"Invalid difficulty level: {current_difficulty}")

        numeric_difficulty = difficulty_map[current_difficulty]

        # Prepare input features
        sample_input = np.array([[accuracy, error_rate, response_time, task_completion_rate,
                                  avg_accuracy, avg_error_rate, avg_response_time, avg_task_completion_rate,
                                  session_id, numeric_difficulty]])

        # Normalize the sample using the saved scaler
        sample_input_scaled = scaler.transform(sample_input)

        # Reshape for LSTM input (batch_size, timesteps, features)
        sample_input_lstm = sample_input_scaled.reshape((1, 1, sample_input_scaled.shape[1]))

        # Extract LSTM Features
        lstm_feature_extractor = Model(inputs=lstm_model.input, outputs=lstm_model.layers[-2].output)
        lstm_features = lstm_feature_extractor.predict(sample_input_lstm)

        # Predict using XGBoost
        predicted_class = xgb_model.predict(lstm_features)[0]

        # Convert prediction to difficulty level
        predicted_difficulty = difficulty_order[int(predicted_class)]

        # Adjust difficulty level based on rolling metrics
        adjusted_difficulty_index = adjust_difficulty({
            'rolling_accuracy': float(accuracy),
            'rolling_error_rate': float(error_rate),
            'rolling_response_time': float(response_time),
            'rolling_completion_rate': float(task_completion_rate),
            'current_difficulty_level': int(numeric_difficulty)
        })

        # Ensure predicted difficulty stays within bounds
        adjusted_difficulty = difficulty_order[adjusted_difficulty_index]

        print(f"Predicted Difficulty: {predicted_difficulty}, Adjusted Difficulty: {adjusted_difficulty}")
        return adjusted_difficulty

    except Exception as e:
        print(f"Error in predict_next_difficulty: {e}")
        return "error"

def adjust_difficulty(row):
    """ Adjust difficulty level based on rolling performance metrics. """
    n_classes = 9  # Total difficulty levels (0-8)
    current_level = row['current_difficulty_level']

    if row['rolling_accuracy'] > 90 and row['rolling_error_rate'] < 5 and row['rolling_response_time'] < 5 and row['rolling_completion_rate'] > 0.9:
        return min(current_level + 1, n_classes - 1)  
    
    elif row['rolling_accuracy'] > 80 and row['rolling_error_rate'] < 15 and row['rolling_response_time'] < 6 and row['rolling_completion_rate'] > 0.8:
        return min(current_level + 1, n_classes - 1)  

    elif row['rolling_accuracy'] < 50 or row['rolling_error_rate'] > 40 or row['rolling_response_time'] > 9 or row['rolling_completion_rate'] < 0.4:
        return max(current_level - 1, 0)  

    elif row['rolling_accuracy'] < 60 or row['rolling_error_rate'] > 30 or row['rolling_response_time'] > 8 or row['rolling_completion_rate'] < 0.5:
        return max(current_level - 1, 0)  

    return current_level  

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

        # Step 2: Retrieve past session data to compute rolling averages
        cursor.execute("""
            SELECT accuracy, error_rate, response_time, task_completion_rate
            FROM performance_metrics
            WHERE learner_id = %s
            ORDER BY session_id DESC
            LIMIT 10
        """, (data['learner_id'],))
        
        sessions = cursor.fetchall()

        if len(sessions) == 0:
            # If no past data, use current session values as averages
            avg_accuracy =  data['accuracy']
            avg_error_rate = data['error_rate']
            avg_response_time = data['response_time']
            avg_task_completion_rate = data['task_completion_rate']
        else:
            # Compute rolling averages from last 5 sessions
            avg_accuracy = np.mean([s[0] for s in sessions[-5:]])
            avg_error_rate = np.mean([s[1] for s in sessions[-5:]])
            avg_response_time = np.mean([s[2] for s in sessions[-5:]])
            avg_task_completion_rate = np.mean([s[3] for s in sessions[-5:]])

        # Step 3: Predict the next difficulty level
        predicted_difficulty = predict_next_difficulty(
            learner_id=data['learner_id'],
            session_id=data['session_id'],
            current_difficulty='Easy 1',  #data['difficulty_level'],
            accuracy=data['accuracy'],
            error_rate=data['error_rate'],
            response_time=data['response_time'],
            task_completion_rate=data['task_completion_rate'],
            avg_accuracy=avg_accuracy,
            avg_error_rate=avg_error_rate,
            avg_response_time=avg_response_time,
            avg_task_completion_rate=avg_task_completion_rate
        )
        current_index = level_index[current_difficulty]
        predicted_index = level_index[predicted_difficulty]
        if predicted_index > current_index + 2:
             predicted_difficulty = difficulty_levels[current_index + 1]
        elif predicted_index < current_index - 3:
             predicted_difficulty = difficulty_levels[current_index - 1]
    
    
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
