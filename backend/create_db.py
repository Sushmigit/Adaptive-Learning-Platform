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
    ("A", "static/sounds/a_sound.mp3"),
    ("B", "static/sounds/b_sound.mp3"),
    ("C", "static/sounds/c_sound.mp3"),
]

cursor.executemany("INSERT INTO sounds (letter, audio_path) VALUES (%s, %s)", data)
conn.commit()
conn.close()

print("Database initialized successfully!")
