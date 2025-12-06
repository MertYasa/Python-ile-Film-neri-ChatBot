import sqlite3

# Chatbot veritabanı oluştur
conn = sqlite3.connect("backend/database/chatbot_data.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS chatbot_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT,
    answer TEXT
)
""")
conn.commit()
conn.close()

# Film veritabanı oluştur
conn = sqlite3.connect("backend/database/movies.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    genre TEXT,
    year INTEGER,
    rating REAL,
    description TEXT
)
""")
conn.commit()
conn.close()
chatbot_examples = [
    ("Merhaba", "Merhaba! Size nasıl yardımcı olabilirim?"),
    ("Nasılsın?", "Ben bir yapay zekayım, duygularım yok ama yardımcı olmaya hazırım!"),
    ("Film önerir misin?", "Tabii, bana favori film türünüzü söyleyin."),
]

conn = sqlite3.connect("backend/database/chatbot_data.db")
cursor = conn.cursor()
cursor.executemany("INSERT INTO chatbot_data (question, answer) VALUES (?, ?)", chatbot_examples)
conn.commit()
conn.close()

movie_examples = [
    ("Inception", "Sci-Fi", 2010, 8.8, "Zihin hırsızlarının hikayesi."),
    ("The Dark Knight", "Action", 2008, 9.0, "Batman ve Joker arasındaki mücadele."),
    ("Interstellar", "Sci-Fi", 2014, 8.6, "Uzay ve zamanın derinliklerine yolculuk."),
]

conn = sqlite3.connect("backend/database/movies.db")
cursor = conn.cursor()
cursor.executemany("INSERT INTO movies (title, genre, year, rating, description) VALUES (?, ?, ?, ?, ?)", movie_examples)
conn.commit()
conn.close()
