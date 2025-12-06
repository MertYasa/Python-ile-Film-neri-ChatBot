import csv
import sqlite3

conn = sqlite3.connect("backend/database/movies.db")
cursor = conn.cursor()

with open("data/clean_movies.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader)  # başlık satırını atla
    for row in reader:
        title, genre, year, rating, description = row
        cursor.execute("""
            INSERT INTO movies (title, genre, year, rating, description)
            VALUES (?, ?, ?, ?, ?)
        """, (title, genre, int(year), float(rating), description))

conn.commit()
conn.close()
print("✅ Temiz film verileri başarıyla yüklendi.")
