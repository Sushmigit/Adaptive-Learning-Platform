import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123Sushmi@123",
    database="letter_sound_db"
)
cursor = conn.cursor()

# Insert data
data = [
    ("bat", "static/sounds/w1.mp3"),
    ("cat", "static/sounds/w2.mp3"),
    ("dog", "static/sounds/w3.mp3"),
]

cursor.executemany("INSERT INTO word_sounds (letter, audio_path) VALUES (%s, %s)", data)
conn.commit()
conn.close()

print("Database initialized successfully!")
